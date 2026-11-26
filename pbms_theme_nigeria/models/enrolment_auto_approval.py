from odoo import fields, models


class NsipaEnrolmentAutoApproval(models.Model):
    _inherit = "g2p.beneficiary.list"

    def _initialize_workflow(self):
        """Enrolment lists need no approval: when a program has no ENROLMENT approval stages, approve the list as
        soon as it is created (the same end state as approving the final stage).

        Without this the list would stay PENDING with no stage to act on, which also blocks creating the next list
        for the cycle ("A list is already in progress"). Disbursement lists are untouched: they still follow the
        program's Disbursement Workflow stages.
        """
        super()._initialize_workflow()
        self.ensure_one()
        if self.list_stage != "enrollment" or not self.program_id:
            return
        has_stages = self.env["g2p.workflow.stage.definition"].sudo().search_count([
            ("program_id", "=", self.program_id.id),
            ("cycle_type", "=", "ENROLMENT"),
        ])
        if has_stages:
            return
        self.workflow_approval_status = "APPROVED"
        self.list_workflow_status = "approved_final_enrolment"
        self.envelope_creation_status = "not_applicable"
        self.approval_date = fields.Date.context_today(self)
        if self.enrollment_cycle_id:
            self.enrollment_cycle_id.sudo().write({"approved_for_enrollment": True})
