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

        # Derive tranche number exclusively from program_mnemonic (Program Name)
        tranche_num = 1
        if program_mnemonic:
            import re
            match = re.search(r'(\d+)', program_mnemonic)
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
                # 1. Update household status in NSR (both main register and child scheme table)
                updated_ids = self._update_nsr_household_status(
                    cur, table_name, target_registry, record_ids, tranche_num,
                    per_beneficiary_amount,
                )

                if not updated_ids:
                    _logger.info("No records found in NSR to update")
                    conn.rollback()
                    return

                # 2. Insert transaction ledger record if not already inserted (Idempotency)
                cur.execute(
                    "SELECT 1 FROM g2p_registry_transaction_ledger WHERE reconciliation_id = %s LIMIT 1;",
                    (envelope_id,)
                )
                if cur.fetchone():
                    _logger.info(
                        "Envelope %s has already been recorded in transaction ledger. Skipping duplicate ledger insert.",
                        envelope_id,
                    )
                else:
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

    def _get_nsr_scheme_table_name(self, target_registry):
        """Derive NSR child scheme applications table name from target_registry string."""
        registry_map = {
            "gramstackhousehold": "g2p_register_gramstack_household_scheme_applications",
            "gramstack_household": "g2p_register_gramstack_household_scheme_applications",
            "household": "g2p_register_household_scheme_applications",
            "individual": "g2p_register_individual_scheme_applications",
            "farmer": "g2p_register_farmer_scheme_applications",
            "student": "g2p_register_student_scheme_applications",
            "group": "g2p_register_group_scheme_applications",
        }
        reg_clean = target_registry.lower().rstrip('s')
        return registry_map.get(
            target_registry.lower(),
            f"g2p_register_{reg_clean}_scheme_applications",
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

    def _update_nsr_household_status(self, cur, table_name, target_registry, record_ids, tranche_num, amount):
        """
        Updates the household status from APPLIED to TRANCHE_X_DISBURSED in NSR,
        both in the main register table and in the scheme_applications child table (which the UI reads).
        Returns list of updated internal_record_ids.
        """
        status_val = f"TRANCHE_{tranche_num}_DISBURSED"

        # 1. Update main register table (e.g. g2p_register_gramstack_households)
        update_query = f"""
            UPDATE {table_name}
            SET status = %s
            WHERE internal_record_id IN %s
            RETURNING internal_record_id;
        """
        cur.execute(update_query, (status_val, tuple(record_ids)))
        rows = cur.fetchall()
        updated_ids = [r[0] for r in rows]

        target_ids = updated_ids if updated_ids else record_ids

        # 2. Update scheme_applications child table (which the UI Applied Schemes tab displays)
        child_scheme_table = self._get_nsr_scheme_table_name(target_registry)
        cur.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s;",
            (child_scheme_table,)
        )
        if cur.fetchone():
            child_update_query = f"""
                UPDATE {child_scheme_table}
                SET status = %s
                WHERE link_internal_record_id IN %s;
            """
            cur.execute(child_update_query, (status_val, tuple(target_ids)))
            _logger.info(
                "Updated %s rows in child table %s to status %s",
                cur.rowcount, child_scheme_table, status_val,
            )

        return target_ids

    def _insert_transaction_ledger(
        self, cur, table_name, target_registry, updated_ids,
        program_mnemonic, cycle_mnemonic, benefit_code_mnemonic,
        tranche_num, amount, measurement_unit, envelope_id, bank_ref,
    ):
        """
        Appends immutable transaction records to g2p_registry_transaction_ledger
        with all values pulled dynamically from NSR + PBMS context.
        Ensures g2p_registry_transaction_ledger exists before inserting.
        """
        create_ledger_table_sql = """
            CREATE TABLE IF NOT EXISTS g2p_registry_transaction_ledger (
                id BIGSERIAL PRIMARY KEY,
                target_registry VARCHAR(64) NOT NULL,
                internal_record_id VARCHAR(128) NOT NULL,
                beneficiary_name VARCHAR(255),
                beneficiary_mobile VARCHAR(32),
                aadhaar_number VARCHAR(64),
                scheme_code VARCHAR(64) NOT NULL,
                scheme_name VARCHAR(255),
                program_mnemonic VARCHAR(128),
                cycle_mnemonic VARCHAR(128),
                tranche_number INT,
                source_system VARCHAR(64) DEFAULT 'PBMS',
                amount NUMERIC(14,2) NOT NULL,
                currency VARCHAR(10) DEFAULT 'INR',
                payment_method VARCHAR(32) DEFAULT 'DBT_BANK',
                bank_account_no VARCHAR(64),
                ifsc VARCHAR(32),
                reconciliation_id VARCHAR(128) NOT NULL,
                bank_reference_number VARCHAR(128),
                transaction_status VARCHAR(32) NOT NULL DEFAULT 'SUCCESS',
                error_reason VARCHAR(255),
                dispatched_at TIMESTAMP WITHOUT TIME ZONE,
                reconciled_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
            );
        """
        cur.execute(create_ledger_table_sql)

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
