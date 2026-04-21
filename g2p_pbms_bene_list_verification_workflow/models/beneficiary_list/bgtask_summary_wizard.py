from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class G2PBGTaskSummaryWizard(models.TransientModel):
    _inherit = "g2p.bgtask.summary.wizard"

    verification_state = fields.Char()

    show_verification_stage_enrolment_button = fields.Boolean(
        compute="_compute_show_verification_stage_enrolment_button"
    )

    show_verification_stage_disbursement_button = fields.Boolean(
        compute="_compute_show_verification_stage_disbursement_button"
    )

    @api.depends("program_id", "verification_ids")
    def _compute_show_verification_stage_enrolment_button(self):
        # TODO: Bypass the verification stage if admin is logged in
        for rec in self:
            show_button = False
            
            program = rec.program_id
            if program and program.verifications_for_enrolment:
                try:
                    required_reviews = int(program.verifications_for_enrolment)
                except (ValueError, TypeError):
                    required_reviews = 0
                verification_count = len(rec.verification_ids)
                if required_reviews > verification_count:
                    if program.entitlement_verification_ids:
                        state, group = program.entitlement_verification_ids.get_details_for_next_verification(rec.verification_state)
                        if group in rec.env.user.groups_id.ids:
                            show_button = True
                    else:
                        show_button = True if rec.env.user.has_group('g2p_pbms.group_beneficiary_list_verifier') else False
            rec.show_verification_stage_enrolment_button = show_button

    @api.depends("program_id", "verification_ids")
    def _compute_show_verification_stage_disbursement_button(self):
        # TODO: Bypass the verification stage if admin is logged in
        for rec in self:
            show_button = False

            program = rec.program_id
            if program and program.verifications_for_disbursement:
                try:
                    required_reviews = int(program.verifications_for_disbursement)
                except (ValueError, TypeError):
                    required_reviews = 0
                verification_count = len(rec.verification_ids)
                if required_reviews > verification_count:
                    if program.disbursement_verification_ids:
                        state, group = program.disbursement_verification_ids.get_details_for_next_verification(rec.verification_state)
                        if group in rec.env.user.groups_id.ids:
                            show_button = True
                    else:
                        show_button = True if rec.env.user.has_group('g2p_pbms.group_beneficiary_list_verifier') else False
            rec.show_verification_stage_disbursement_button = show_button

    def action_record_verifications(self):
        allowed_group = 'g2p_pbms.group_beneficiary_list_verifier'
        if not self.env.user.has_group(allowed_group):
            raise AccessError(_("You are not allowed to perform this action."))
        
        program = self.program_id
        if not program:
            raise UserError(_("No program is linked to this record."))

        if self.list_stage == 'enrollment' and self.list_workflow_status!='approved_final_enrolment' and program.auto_approve_enrolment:
            self.approve_final_enrollment()
        elif self.list_stage == 'disbursement' and self.list_workflow_status!='approved_for_disbursement' and program.auto_approve_disbursement:
            self.approve_for_disbursement()
        
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add a Verification',
            'res_model': 'storage.file',
            'view_mode': 'form',
            'view_id': self.env.ref('g2p_pbms.view_g2p_beneficiary_list_verification_form').id,
            'target': 'new',
            'context': {
                'default_beneficiary_list_id': self.beneficiary_list_id,
                'beneficiary_list_verification_form_edit': True,
                'wizard_id': self.id,  # Pass wizard ID for verification state updates
            },
        }

    def update_verification_state(self, new_state):
        """Update verification state when verification is completed"""
        self.verification_state = new_state
        # Update the beneficiary list verification state as well
        if self.beneficiary_list_id:
            self.env['g2p.beneficiary.list'].browse(self.beneficiary_list_id).verification_state = new_state


    def action_export_beneficiaries_csv(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/g2p_pbms/export/beneficiaries/%s" % self.id,
            "target": "self",
        }

    @api.model
    def get_beneficiaries(self, wizard_id, page, page_size, odoo_domain, sql_query=None):
        """
        Optimized version of get_beneficiaries that supports precomputed SQL queries
        and increases timeout for large-scale exports (100k+ records).
        """
        wizard = self.sudo().browse(wizard_id)
        api_url = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.staff_portal_api_url')
        sender_id = self.env['ir.config_parameter'].sudo().get_param('g2p_pbms.keymanager_sign_application_id')

        if not api_url:
            _logger.error("API URL not set in environment")

        order_by_condition = "id asc"
        if sql_query is None:
            # Fallback to the base calculation if no query is provided
            sql_query, order_by_condition = self._build_sql_query(odoo_domain, wizard.target_registry)

        endpoint = f"{api_url}/search_beneficiaries"
        payload = {
            "signature": "string",
            "header": {
                "version": "1.0.0",
                "message_id": "string",
                "message_ts": "string",
                "action": "search_beneficiaries",
                "sender_id": sender_id,
                "sender_uri": "",
                "receiver_id": "",
                "total_count": 0,
                "is_msg_encrypted": False,
                "meta": "string"
            },
            "message": {
                "beneficiary_list_id": wizard.beneficiary_list_uuid,
                "target_registry": wizard.target_registry,
                "page": page,
                "page_size": page_size,
                "search_query": sql_query or "",
                "order_by": order_by_condition or "id asc",
            }
        }

        jwt_token = self.env['keymanager.provider'].jwt_sign_keymanager(
            json.dumps(payload, indent=None, separators=(",", ":"), sort_keys=True)
        )
        headers = {
            "content-type": "application/json",
            "Signature": jwt_token
        }
        try:
            # Increased timeout to 60s for large-scale batches
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            response_json = response.json()
        except Exception as e:
            _logger.error("API call failed in extension override: %s", e)
            return {
                "message": {
                    "total_beneficiary_count": 0,
                    "page": page,
                    "page_size": page_size,
                    "beneficiaries": []
                }
            }
        return response_json

