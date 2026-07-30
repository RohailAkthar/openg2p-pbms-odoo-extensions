from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError


class G2PBGTaskSummaryWizard(models.TransientModel):
    _inherit = "g2p.bgtask.summary.wizard"

    verification_state = fields.Char()

    show_verification_stage_disbursement_button = fields.Boolean(
        compute="_compute_show_verification_stage_disbursement_button"
    )

    @api.depends("program_id", "verification_ids")
    def _compute_show_verification_stage_disbursement_button(self):
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

        if self.list_stage == 'enrollment' and self.list_workflow_status != 'approved_final_enrolment' and program.auto_approve_enrolment:
            self.approve_final_enrollment()
        elif self.list_stage == 'disbursement' and self.list_workflow_status != 'approved_for_disbursement' and program.auto_approve_disbursement:
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
                'wizard_id': self.id,
            },
        }

    def update_verification_state(self, new_state):
        """Update verification state when verification is completed"""
        self.verification_state = new_state
        if self.beneficiary_list_id:
            self.env['g2p.beneficiary.list'].browse(self.beneficiary_list_id).verification_state = new_state
