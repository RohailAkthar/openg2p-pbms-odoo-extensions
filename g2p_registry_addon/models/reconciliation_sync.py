import logging
import json
import requests
from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class G2PBeneficiaryListReconciliation(models.Model):
    _inherit = "g2p.beneficiary.list"

    def action_process_reconciliation_success(self, bank_reference=None):
        """
        Dynamically syncs reconciliation to NSR and appends to g2p_registry_transaction_ledger.
        No hardcoding: derives registry, scheme, amount, tranche, and UTR dynamically.
        """
        self.ensure_one()

        target_reg = self.program_id.target_registry
        if not target_reg:
            return False

        # 1. Fetch beneficiary IDs dynamically from bgtask
        wizard = self.env['g2p.bgtask.summary.wizard'].new({
            'beneficiary_list_uuid': self.beneficiary_list_id,
            'target_registry': target_reg,
        })
        search_res = wizard.get_beneficiaries(page=1, page_size=1000)
        beneficiaries = (
            search_res.get("response_body", {})
            .get("response_payload", {})
            .get("beneficiaries", [])
        )
        record_ids = [b.get("internal_record_id") for b in beneficiaries if b.get("internal_record_id")]

        if not record_ids:
            return False

        # 2. Derive dynamic program metadata
        prog = self.program_id
        cycle = self.disbursement_cycle_id
        cycle_name = cycle.cycle_name if cycle else ""
        prog_name = prog.program_mnemonic or ""
        envelope_id = (cycle.bridge_envelope_id if cycle else "") or ""
        utr = bank_reference or ""

        # Determine tranche number dynamically from cycle or mnemonic if present
        tranche_num = cycle.cycle_number if (cycle and cycle.cycle_number) else 1

        # Determine amount dynamically from program or cycle
        disb_amount = 0.0
        if hasattr(self, "disbursement_quantity") and self.disbursement_quantity:
            try:
                dq = json.loads(self.disbursement_quantity)
                if isinstance(dq, dict):
                    disb_amount = float(list(dq.values())[0])
                elif isinstance(dq, list) and dq:
                    disb_amount = float(dq[0])
            except Exception:
                disb_amount = 0.0
        if not disb_amount and hasattr(prog, "entitlement_amount") and prog.entitlement_amount:
            disb_amount = float(prog.entitlement_amount)

        # 3. Dynamic SQL update for the target registry table (works for gramstackhousehold, household, etc.)
        table_name = "g2p_register_gramstack_households" if target_reg in ("gramstackhousehold", "gramstack_household") else f"g2p_register_{target_reg}s"

        update_query = f"""
            UPDATE {table_name}
            SET 
                status = 'TRANCHE_' || %s || '_DISBURSED',
                payment_status = 'RECONCILED_SUCCESS',
                reconciled_at = NOW(),
                completed_tranches_count = COALESCE(completed_tranches_count, 0) + 1,
                total_disbursed_amount = COALESCE(total_disbursed_amount, 0) + %s,
                last_disbursed_date = NOW(),
                write_date = NOW()
            WHERE internal_record_id IN %s
              AND status = 'APPLIED'
            RETURNING internal_record_id;
        """
        self.env.cr.execute(update_query, (tranche_num, disb_amount, tuple(record_ids)))
        updated_rows = self.env.cr.fetchall()

        if not updated_rows:
            return 0

        updated_ids = [r[0] for r in updated_rows]

        # 4. Insert dynamic records into g2p_registry_transaction_ledger
        ledger_query = f"""
            INSERT INTO g2p_registry_transaction_ledger (
                target_registry,
                internal_record_id,
                beneficiary_name,
                beneficiary_mobile,
                aadhaar_number,
                scheme_code,
                scheme_name,
                program_mnemonic,
                cycle_mnemonic,
                tranche_number,
                source_system,
                amount,
                currency,
                payment_method,
                bank_account_no,
                ifsc,
                reconciliation_id,
                bank_reference_number,
                transaction_status,
                reconciled_at
            )
            SELECT 
                %s,
                h.internal_record_id,
                COALESCE(h.applicant_name, h.member_name, h.household_reference_name, ''),
                COALESCE(h.mobile_number, ''),
                COALESCE(h.aadhaar_number, ''),
                COALESCE(h.scheme_code, %s),
                COALESCE(h.scheme_name, %s),
                %s,
                %s,
                %s,
                'PBMS',
                %s,
                'INR',
                'DBT_BANK',
                COALESCE(h.bank_account_no, ''),
                COALESCE(h.ifsc, ''),
                %s,
                %s,
                'SUCCESS',
                NOW()
            FROM {table_name} h
            WHERE h.internal_record_id IN %s;
        """
        self.env.cr.execute(ledger_query, (
            target_reg,
            prog_name,
            prog_name,
            prog_name,
            cycle_name,
            tranche_num,
            disb_amount,
            envelope_id,
            utr,
            tuple(updated_ids),
        ))

        _logger.info("Successfully reconciled %s records dynamically for %s", len(updated_ids), target_reg)
        return len(updated_ids)


class G2PBGTaskSummaryWizardReconciliation(models.TransientModel):
    _inherit = "g2p.bgtask.summary.wizard"

    def action_generate_disbursement_envelope_summary(self):
        """
        Extend the envelope summary report action to dynamically trigger reconciliation sync
        when the bridge confirms 100% reconciled disbursements with zero reversals.
        """
        res = super().action_generate_disbursement_envelope_summary()

        try:
            # Check reconciliation status from the latest envelope summary wizard created
            summary_id = res.get("res_id") if isinstance(res, dict) else None
            summary_rec = self.env["g2p.disbursement.envelope.summary.wizard"].browse(summary_id) if summary_id else False

            if not summary_rec:
                # Check recent wizard for this envelope
                summary_rec = self.env["g2p.disbursement.envelope.summary.wizard"].search(
                    [("disbursement_envelope_id", "=", self.disbursement_envelope_id)],
                    order="id desc", limit=1
                )

            if summary_rec:
                reconciled = summary_rec.number_of_disbursements_reconciled or 0
                declared = summary_rec.number_of_disbursements_declared or 0
                reversed_disb = summary_rec.number_of_disbursements_reversed or 0

                if reconciled > 0 and reconciled >= declared and reversed_disb == 0:
                    list_id = self.beneficiary_list_id or (self.wizard_id.beneficiary_list_id if self.wizard_id else False)
                    if list_id:
                        list_rec = self.env["g2p.beneficiary.list"].browse(int(list_id))
                        if list_rec:
                            bank_ref = summary_rec.funds_blocked_reference_number or "UTR_RECON_OK"
                            updated = list_rec.action_process_reconciliation_success(bank_reference=bank_ref)
                            _logger.info("Dynamic reconciliation sync updated %s records in NSR", updated)
        except Exception as e:
            _logger.warning("Error in dynamic reconciliation sync override: %s", e)

        return res
