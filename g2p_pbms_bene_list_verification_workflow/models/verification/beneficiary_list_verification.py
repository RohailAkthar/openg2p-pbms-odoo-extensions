from odoo import models, fields, api


class G2PBeneficiaryListVerification(models.Model):
    _inherit = "storage.file"

    @api.model
    def create(self, vals):
        """Override create to update verification state when verification is completed"""
        result = super().create(vals)

        # Check if this is a beneficiary list verification
        # beneficiary_list_id comes from context, not vals
        beneficiary_list_id = self.env.context.get('default_beneficiary_list_id')
        if beneficiary_list_id:
            beneficiary_list = self.env['g2p.beneficiary.list'].browse(beneficiary_list_id)
            wizard_id = self.env.context.get('wizard_id')
            
            if wizard_id:
                wizard = self.env['g2p.bgtask.summary.wizard'].browse(wizard_id)
                # Get the next verification state based on current state
                if wizard.list_stage == 'enrollment':
                    verification_rules = wizard.program_id.entitlement_verification_ids
                elif wizard.list_stage == 'disbursement':
                    verification_rules = wizard.program_id.disbursement_verification_ids
                else:
                    verification_rules = None
                if verification_rules:
                    # Get next verification state
                    next_state, next_group = verification_rules.get_details_for_next_verification(wizard.verification_state)
                    # Update verification state
                    wizard.update_verification_state(next_state)
                    
        return result
