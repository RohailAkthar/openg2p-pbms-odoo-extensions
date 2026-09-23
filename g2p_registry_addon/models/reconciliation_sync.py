import logging
import json
import os
import psycopg2
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class G2PDisbursementEnvelopeLineNSRSync(models.TransientModel):
    """
    Extends G2PAPIDisbursementEnvelopeLine to sync reconciliation
    results directly to the NSR database using psycopg2.
    """
    _inherit = "g2p.api.disbursement.envelope.line"

    def _get_nsr_connection(self):
        """
        Creates a psycopg2 connection to the NSR database.
        Reads host/port/dbname/user from ir.config_parameter (with env var fallbacks).
        Password comes exclusively from the NSR_DB_PASSWORD environment variable,
        which is mounted from K8s secret 'nsr' key 'nsr-db-user'.
        """
        ICP = self.env["ir.config_parameter"].sudo()
        host = ICP.get_param(
            "g2p_registry_addon.nsr_db_host",
            os.getenv("NSR_DB_HOST", "commons-postgresql"),
        )
        port = ICP.get_param(
            "g2p_registry_addon.nsr_db_port",
            os.getenv("NSR_DB_PORT", "5432"),
        )
        dbname = ICP.get_param(
            "g2p_registry_addon.nsr_db_name",
            os.getenv("NSR_DB_NAME", "nsr"),
        )
        user = ICP.get_param(
            "g2p_registry_addon.nsr_db_user",
            os.getenv("NSR_DB_USER", "nsr_user"),
        )
        # Password from K8s secret via env var only — never stored in Odoo DB
        password = os.getenv("NSR_DB_PASSWORD", "")

        if not password:
            _logger.warning(
                "NSR_DB_PASSWORD environment variable is not set. "
                "Ensure the PBMS deployment mounts K8s secret 'nsr' key 'nsr-db-user' "
                "as NSR_DB_PASSWORD."
            )

        _logger.info(
            "Connecting to NSR database: host=%s port=%s dbname=%s user=%s",
            host, port, dbname, user,
        )
        return psycopg2.connect(
            host=host,
            port=int(port),
            dbname=dbname,
            user=user,
            password=password,
        )

    def action_view_disbursement_envelope(self):
        """
        Override to trigger NSR sync after the envelope summary is fetched.
        Calls super() first (which fetches reconciliation data from G2P Bridge),
        then checks if reconciliation is complete (reconciled > 0, reversed == 0).
        If so, updates NSR household status and appends to transaction ledger.
        """
        # Call the original method — this fetches from G2P Bridge and creates
        # the disbursement.envelope.summary.wizard record
        res = super().action_view_disbursement_envelope()

        try:
            self._sync_reconciliation_to_nsr(res)
        except Exception as e:
            _logger.error(
                "NSR reconciliation sync failed for envelope %s: %s",
                self.disbursement_envelope_id, e,
                exc_info=True,
            )
            # Don't break the existing flow — just log the error

        return res

    def _sync_reconciliation_to_nsr(self, action_result):
        """
        Checks the summary wizard created by super() for reconciliation status.
        If all disbursements are reconciled with zero reversals, updates NSR.
        """
        # Extract the summary wizard record from the action result
        summary_rec = None
        if isinstance(action_result, dict):
            res_id = action_result.get("res_id") or action_result.get("data", {}).get("ids", [None])[0] if action_result.get("data") else action_result.get("res_id")
            if res_id:
                summary_rec = self.env["g2p.disbursement.envelope.summary.wizard"].browse(res_id)

        if not summary_rec:
            # Try searching for the latest summary for this envelope
            summary_rec = self.env["g2p.disbursement.envelope.summary.wizard"].search(
                [("disbursement_envelope_id", "=", self.disbursement_envelope_id)],
                order="id desc",
                limit=1,
            )

        if not summary_rec:
            _logger.debug("No summary wizard found for envelope %s", self.disbursement_envelope_id)
            return

        reconciled = summary_rec.number_of_disbursements_reconciled or 0
        declared = summary_rec.number_of_disbursements_declared or 0
        reversed_disb = summary_rec.number_of_disbursements_reversed or 0

        _logger.info(
            "Envelope %s status: reconciled=%s, declared=%s, reversed=%s",
            self.disbursement_envelope_id, reconciled, declared, reversed_disb,
        )

        # Only sync if fully reconciled with zero reversals
        if reconciled <= 0 or reconciled < declared or reversed_disb > 0:
            _logger.info(
                "Reconciliation not complete for envelope %s. Skipping NSR sync.",
                self.disbursement_envelope_id,
            )
            return

        # Gather dynamic metadata from the envelope line
        target_registry = self.wizard_id.target_registry if self.wizard_id else ""
        if not target_registry:
            _logger.warning("No target_registry found, skipping NSR sync")
            return

        program_mnemonic = self.benefit_program_mnemonic or ""
        cycle_mnemonic = self.cycle_code_mnemonic or ""
        benefit_code_mnemonic = self.benefit_code_mnemonic or ""
        envelope_id = self.disbursement_envelope_id or ""
        disbursement_cycle_id = self.disbursement_cycle_id or ""
        number_of_beneficiaries = self.number_of_beneficiaries or 0
        total_quantity = self.total_disbursement_quantity or 0.0
        measurement_unit = self.measurement_unit or "INR"
        funds_blocked_ref = summary_rec.funds_blocked_reference_number or ""

        # Compute per-beneficiary amount dynamically
        per_beneficiary_amount = 0.0
        if number_of_beneficiaries > 0 and total_quantity > 0:
            per_beneficiary_amount = total_quantity / number_of_beneficiaries

        # Derive tranche number from cycle_mnemonic if possible (e.g. "TRANCHE_1")
        tranche_num = 1
        if cycle_mnemonic:
            import re
            match = re.search(r'(\d+)', cycle_mnemonic)
            if match:
                tranche_num = int(match.group(1))

        # Determine NSR table name dynamically
        table_name = self._get_nsr_table_name(target_registry)

        # Get beneficiary internal_record_ids from the bg-task staff portal API
        record_ids = self._fetch_beneficiary_record_ids(target_registry)
        if not record_ids:
            _logger.warning("No beneficiary record_ids found for registry %s", target_registry)
            return

        # Connect to NSR and run updates
        conn = self._get_nsr_connection()
        try:
            with conn.cursor() as cur:
                # 1. Update household status in NSR
                updated_ids = self._update_nsr_household_status(
                    cur, table_name, record_ids, tranche_num,
                    per_beneficiary_amount,
                )

                if not updated_ids:
                    _logger.info("No APPLIED records found in NSR to update")
                    conn.rollback()
                    return

                # 2. Insert transaction ledger records
                self._insert_transaction_ledger(
                    cur, table_name, target_registry, updated_ids,
                    program_mnemonic, cycle_mnemonic, benefit_code_mnemonic,
                    tranche_num, per_beneficiary_amount, measurement_unit,
                    envelope_id, funds_blocked_ref,
                )

            conn.commit()
            _logger.info(
                "Successfully synced %s records to NSR for envelope %s",
                len(updated_ids), envelope_id,
            )
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _get_nsr_table_name(self, target_registry):
        """Derive NSR table name from target_registry string."""
        registry_map = {
            "gramstackhousehold": "g2p_register_gramstack_households",
            "gramstack_household": "g2p_register_gramstack_households",
            "household": "g2p_register_households",
            "individual": "g2p_register_individuals",
            "farmer": "g2p_register_farmers",
            "student": "g2p_register_students",
            "group": "g2p_register_groups",
        }
        return registry_map.get(
            target_registry.lower(),
            f"g2p_register_{target_registry.lower()}s",
        )

    def _fetch_beneficiary_record_ids(self, target_registry):
        """
        Fetch beneficiary internal_record_ids via the bg-task staff portal API
        (same HTTP call the wizard uses).
        """
        try:
            wizard = self.wizard_id
            if not wizard:
                _logger.warning("No wizard_id available on envelope line")
                return []

            search_result = wizard.get_beneficiaries(
                wizard_id=wizard.id,
                page=1,
                page_size=10000,
                odoo_domain=[],
            )
            beneficiaries = (
                search_result.get("response_body", {})
                .get("response_payload", {})
                .get("beneficiaries", [])
            )
            record_ids = [
                b.get("internal_record_id")
                for b in beneficiaries
                if b.get("internal_record_id")
            ]
            _logger.info("Fetched %s beneficiary record_ids from staff portal", len(record_ids))
            return record_ids
        except Exception as e:
            _logger.error("Failed to fetch beneficiary record_ids: %s", e)
            return []

    def _update_nsr_household_status(self, cur, table_name, record_ids, tranche_num, amount):
        """
        Updates the household status from APPLIED to TRANCHE_X_DISBURSED in NSR.
        Returns list of updated internal_record_ids.
        """
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
        cur.execute(update_query, (str(tranche_num), amount, tuple(record_ids)))
        rows = cur.fetchall()
        return [r[0] for r in rows]

    def _insert_transaction_ledger(
        self, cur, table_name, target_registry, updated_ids,
        program_mnemonic, cycle_mnemonic, benefit_code_mnemonic,
        tranche_num, amount, measurement_unit, envelope_id, bank_ref,
    ):
        """
        Appends immutable transaction records to g2p_registry_transaction_ledger
        with all values pulled dynamically from NSR + PBMS context.
        """
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
                reconciled_at,
                created_at
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
                %s,
                'DBT_BANK',
                COALESCE(h.bank_account_no, ''),
                COALESCE(h.ifsc, ''),
                %s,
                %s,
                'SUCCESS',
                NOW(),
                NOW()
            FROM {table_name} h
            WHERE h.internal_record_id IN %s;
        """
        cur.execute(ledger_query, (
            target_registry,
            benefit_code_mnemonic or program_mnemonic,
            program_mnemonic,
            program_mnemonic,
            cycle_mnemonic,
            tranche_num,
            amount,
            measurement_unit,
            envelope_id,
            bank_ref,
            tuple(updated_ids),
        ))
        _logger.info(
            "Inserted %s rows into g2p_registry_transaction_ledger",
            cur.rowcount,
        )
