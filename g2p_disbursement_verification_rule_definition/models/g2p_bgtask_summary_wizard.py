from odoo import models, fields, api


class G2PBGTaskSummaryWizard(models.TransientModel):
    _inherit = "g2p.bgtask.summary.wizard"

    show_verification_stage_disbursement_button = fields.Boolean(
        compute="_compute_show_verification_stage_disbursement_button"
    )

    @api.depends("program_id", "verification_ids")
    def _compute_show_verification_stage_disbursement_button(self):
        for rec in self:
            rec.show_verification_stage_disbursement_button = False
            if rec.list_stage == "disbursement" and rec.list_workflow_status == "initiated":
                 # We need to access the rule definition model to get the next step
                RuleModel = self.program_id.disbursement_verification_ids
                
                # Fetch next verification details based on current verification_state
                # Note: verification_state field is defined in the entitlement wizard extension or base?
                # User request says: "verification_state -> value will be computed from verification rule definition table"
                # in `g2p.bgtask.summary.wizard` model -> update
                # Since we split the wizard extension, both use the same underlying model `g2p.bgtask.summary.wizard`.
                # `verification_state` was added in the entitlement extension file, but it's on the same model so available here.
                
                next_step = RuleModel.get_details_for_next_verification(rec.verification_state)
                
                if next_step:
                    next_group_id = next_step.get("group_id")
                    if next_group_id in self.env.user.groups_id.ids:
                         rec.show_verification_stage_disbursement_button = True

    def action_record_verifications(self):
        
        program = self.program_id
        if not program:
            raise UserError(_("No program is linked to this record."))

        if self.list_stage == 'enrollment' and self.list_workflow_status!='approved_final_enrolment' and program.auto_approve_enrolment:
            self.approve_final_enrollment(self)
        elif self.list_stage == 'disbursement' and self.list_workflow_status!='approved_for_disbursement' and program.auto_approve_disbursement:
            self.approve_for_disbursement(self)
        
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
            },
        }

