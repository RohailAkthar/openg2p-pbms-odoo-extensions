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

    def _fetch_reconciliation_details_from_bridge(self, envelope_id):
        """
        Queries G2P Bridge Partner API /get_envelope_reconciliation_details over HTTP.
        Returns a tuple: (reconciled_beneficiary_ids, reversed_map)
        where reversed_map is {beneficiary_id: {'reason': ..., 'bank_ref': ...}}
        """
        import requests
        try:
            api_url = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.g2p_bridge_api_url')
            if not api_url:
                _logger.warning("g2p_bridge_api_url is not set in ir.config_parameter")
                return [], {}

            endpoint = f"{api_url.rstrip('/')}/get_envelope_reconciliation_details"
            _logger.info("Calling G2P Bridge API: %s with envelope_id=%s", endpoint, envelope_id)

            payload = {"envelope_id": envelope_id}
            response = requests.post(endpoint, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()

            reconciled_ids = data.get("reconciled_beneficiary_ids", [])
            reversed_list = data.get("reversed_beneficiaries", [])
            reversed_map = {
                item["beneficiary_id"]: {
                    "reason": item.get("reversal_reason") or "PAYMENT_REVERSED_BY_BANK",
                    "bank_ref": item.get("bank_reference") or "",
                }
                for item in reversed_list
                if item.get("beneficiary_id")
            }

            _logger.info(
                "Fetched bridge recon via API for envelope %s: %s reconciled, %s reversed",
                envelope_id, len(reconciled_ids), len(reversed_map),
            )
            return reconciled_ids, reversed_map
        except Exception as e:
            _logger.warning(
                "Could not fetch per-beneficiary recon from Bridge API for envelope %s: %s",
                envelope_id, e,
            )
            return [], {}

    def action_view_disbursement_envelope(self):
        """
        Override to trigger NSR sync after the envelope summary is fetched.
        Calls super() first (which fetches reconciliation data from G2P Bridge),
        then checks if reconciliation data exists.
        Updates NSR household status (reconciled -> DISBURSED, reversed -> PAYMENT_FAILED)
        and appends to transaction ledger.
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
        Supports partial reconciliation: updates reconciled to DISBURSED,
        and reversals to PAYMENT_FAILED in NSR.
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

        # Proceed if at least one payment is reconciled or reversed
        if reconciled <= 0 and reversed_disb <= 0:
            _logger.info(
                "No reconciliations or reversals yet for envelope %s. Skipping NSR sync.",
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
        child_scheme_table = self._get_nsr_scheme_table_name(target_registry)

        # Get beneficiary internal_record_ids from the bg-task staff portal API
        all_record_ids = self._fetch_beneficiary_record_ids(target_registry)
        if not all_record_ids:
            _logger.warning("No beneficiary record_ids found for registry %s", target_registry)
            return

        # Fetch per-beneficiary recon details from Bridge DB
        bridge_reconciled_ids, bridge_reversed_map = self._fetch_reconciliation_details_from_bridge(envelope_id)

        # Determine which IDs are reconciled and which are reversed
        reconciled_ids = []
        reversed_map = {}

        if bridge_reconciled_ids or bridge_reversed_map:
            reconciled_ids = [rid for rid in bridge_reconciled_ids if rid in all_record_ids] or bridge_reconciled_ids
            reversed_map = {bid: val for bid, val in bridge_reversed_map.items() if bid in all_record_ids} or bridge_reversed_map
        else:
            # Fallback if bridge query returned nothing (e.g., bridge DB not directly accessible)
            if reversed_disb == 0 and reconciled >= declared:
                reconciled_ids = all_record_ids
            else:
                _logger.warning(
                    "Envelope %s has partial reconciliation (%s reconciled, %s reversed) "
                    "but Bridge DB returned no individual records. Cannot distinguish succeeded from failed beneficiaries.",
                    envelope_id, reconciled, reversed_disb,
                )
                return

        # Connect to NSR and run updates
        conn = self._get_nsr_connection()
        try:
            with conn.cursor() as cur:
                # 1. Update Reconciled Beneficiaries to TRANCHE_X_DISBURSED
                if reconciled_ids:
                    status_disbursed = f"TRANCHE_{tranche_num}_DISBURSED"
                    update_query = f"""
                        UPDATE {table_name}
                        SET status = %s
                        WHERE internal_record_id IN %s;
                    """
                    cur.execute(update_query, (status_disbursed, tuple(reconciled_ids)))

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
                        cur.execute(child_update_query, (status_disbursed, tuple(reconciled_ids)))
                        _logger.info(
                            "Updated %s rows in child table %s to status %s",
                            cur.rowcount, child_scheme_table, status_disbursed,
                        )

                    # Insert SUCCESS in transaction ledger
                    self._insert_transaction_ledger(
                        cur, table_name, target_registry, reconciled_ids,
                        program_mnemonic, cycle_mnemonic, benefit_code_mnemonic,
                        tranche_num, per_beneficiary_amount, measurement_unit,
                        envelope_id, funds_blocked_ref, transaction_status="SUCCESS",
                    )

                # 2. Update Reversed Beneficiaries to TRANCHE_X_PAYMENT_FAILED
                if reversed_map:
                    status_failed = f"TRANCHE_{tranche_num}_PAYMENT_FAILED"
                    for ben_id, rev_info in reversed_map.items():
                        err_reason = rev_info.get("reason") or "PAYMENT_REVERSED_BY_BANK"
                        # Update main register table
                        cur.execute(f"""
                            UPDATE {table_name}
                            SET status = %s,
                                record_status_reason = %s
                            WHERE internal_record_id = %s;
                        """, (status_failed, err_reason, ben_id))

                        # Update child scheme table
                        cur.execute(
                            "SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = %s;",
                            (child_scheme_table,)
                        )
                        if cur.fetchone():
                            cur.execute(f"""
                                UPDATE {child_scheme_table}
                                SET status = %s,
                                    record_status_reason = %s
                                WHERE link_internal_record_id = %s;
                            """, (status_failed, err_reason, ben_id))

                    # Insert FAILED in transaction ledger
                    self._insert_transaction_ledger(
                        cur, table_name, target_registry, list(reversed_map.keys()),
                        program_mnemonic, cycle_mnemonic, benefit_code_mnemonic,
                        tranche_num, per_beneficiary_amount, measurement_unit,
                        envelope_id, funds_blocked_ref, transaction_status="FAILED",
                        reversed_map=reversed_map,
                    )

            conn.commit()
            _logger.info(
                "Successfully synced reconciliation to NSR for envelope %s: %s reconciled, %s reversed",
                envelope_id, len(reconciled_ids), len(reversed_map),
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

    def _insert_transaction_ledger(
        self, cur, table_name, target_registry, target_ids,
        program_mnemonic, cycle_mnemonic, benefit_code_mnemonic,
        tranche_num, amount, measurement_unit, envelope_id, bank_ref,
        transaction_status="SUCCESS", reversed_map=None,
    ):
        """
        Appends immutable transaction records to g2p_registry_transaction_ledger
        with all values pulled dynamically from NSR + PBMS context.
        Supports both SUCCESS and FAILED transaction records.
        """
        if not target_ids:
            return

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

        for target_id in target_ids:
            # Check idempotency per beneficiary and reconciliation_id and transaction_status
            cur.execute(
                """
                SELECT 1 FROM g2p_registry_transaction_ledger 
                WHERE reconciliation_id = %s 
                  AND internal_record_id = %s 
                  AND transaction_status = %s 
                LIMIT 1;
                """,
                (envelope_id, target_id, transaction_status)
            )
            if cur.fetchone():
                continue

            err_reason = None
            specific_bank_ref = bank_ref
            if reversed_map and target_id in reversed_map:
                err_reason = reversed_map[target_id].get("reason")
                specific_bank_ref = reversed_map[target_id].get("bank_ref") or bank_ref

            ledger_insert_sql = f"""
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
                    error_reason,
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
                    %s,
                    %s,
                    NOW(),
                    NOW()
                FROM {table_name} h
                WHERE h.internal_record_id = %s;
            """
            cur.execute(ledger_insert_sql, (
                target_registry,
                benefit_code_mnemonic or program_mnemonic,
                program_mnemonic,
                program_mnemonic,
                cycle_mnemonic,
                tranche_num,
                amount,
                measurement_unit,
                envelope_id,
                specific_bank_ref,
                transaction_status,
                err_reason,
                target_id,
            ))

        _logger.info(
            "Inserted %s rows (%s) into g2p_registry_transaction_ledger for envelope %s",
            len(target_ids), transaction_status, envelope_id,
        )
