from odoo import models, fields


class G2PBeneficiaryList(models.Model):
    _inherit = "g2p.beneficiary.list"

    verification_state = fields.Char()

    def action_open_summary_wizard(self):
        self.ensure_one()
        wizard_vals = {
            "target_registry": self.program_id.target_registry,
            "mnemonic": self.mnemonic,
            "brief": self.brief,
            "program_id": self.program_id.id,
            "beneficiary_list_id": self.id,
            "beneficiary_list_uuid": self.beneficiary_list_id,
            "enrollment_cycle_id": self.enrollment_cycle_id,
            "disbursement_cycle_id": self.disbursement_cycle_id,
            "list_stage": self.list_stage,
            "list_workflow_status": self.list_workflow_status,
            "enrollment_start_date": self.enrollment_cycle_id.enrollment_start_date if self.enrollment_cycle_id else None,
            "enrollment_end_date": self.enrollment_cycle_id.enrollment_end_date if self.enrollment_cycle_id else None,
            "disbursement_cycle_mnemonic": self.disbursement_cycle_id.cycle_mnemonic if self.disbursement_cycle_id else None,
            "approved_for_disbursement": self.disbursement_cycle_id.approved_for_disbursement if self.disbursement_cycle_id else None,
            "verification_state": self.verification_state,
        }

        wizard = self.env["g2p.bgtask.summary.wizard"].create(wizard_vals)
        return {
            "name": "Eligibility Summary Details",
            "view_mode": "form",
            "res_model": "g2p.bgtask.summary.wizard",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "target": "current",
            'context': {
                'default_target_registry': self.program_id.target_registry,
                'default_program_id': self.program_id.id,
                'default_beneficiary_list_id': self.beneficiary_list_id,
            },
        }
