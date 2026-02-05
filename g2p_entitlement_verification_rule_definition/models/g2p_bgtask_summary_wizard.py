from odoo import models, fields, api


class G2PBGTaskSummaryWizard(models.TransientModel):
    _inherit = "g2p.bgtask.summary.wizard"

    verification_state = fields.Char(string="Verification State")

    show_verification_stage_enrolment_button = fields.Boolean(
        compute="_compute_show_verification_stage_enrolment_button"
    )

    @api.depends("program_id", "verification_ids")
    def _compute_show_verification_stage_enrolment_button(self):
        for rec in self:
            rec.show_verification_stage_enrolment_button = False
            if rec.list_stage == "enrollment" and rec.list_workflow_status == "initiated":
                # Get the sequence of the current verification stage
                # Since 'verification_state' stores the state string, passed to get_details_for_next_verification
                
                # We need to access the rule definition model to get the next step
                RuleModel = self.program_id.entitlement_verification_ids
                
                # Fetch next verification details based on current verification_state
                next_step = RuleModel.get_details_for_next_verification(rec.verification_state)
                
                if next_step:
                    # Check if the next step is already the current state (meaning we are at the end appropriately handled by logic)
                    # Requirement says:
                    # if user.group == group: show_button = True
                    
                    next_group_id = next_step.get("group_id")
                    
                    # Check if current user belongs to the required group
                    #if self.env.user.has_group(f"base.group_user"): # We need to check against the specific group ID
                         # has_group takes an xml_id provided by the module, or we can check via user.groups_id
                         # Since we have the group ID integer:
                    if next_group_id in self.env.user.groups_id.ids:
                        rec.show_verification_stage_enrolment_button = True

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

