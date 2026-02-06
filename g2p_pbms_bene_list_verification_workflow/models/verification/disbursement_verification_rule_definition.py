from odoo import models, fields, api

class G2PDisbursementVerificationRuleDefinition(models.Model):
    _name = 'g2p.disbursement.verification.rule.definition'
    _description = 'G2P Disbursement Verification Rule Definition'

    sequence = fields.Integer(string='Sequence', default=10)
    state = fields.Char(string='Stage')
    group_id = fields.Many2one('res.groups', string='User Group')
    
    program_definition_id = fields.Many2one(
        "g2p.program.definition",
            string="Program",
            required=True,
            ondelete="cascade",
        )

    @api.model
    def get_details_for_next_verification(self, previous_state=None):
        """Get next verification details from this program's rules"""
        rules = self.sorted("sequence") if self else self

        if not rules:
            return False

        # First verification stage
        if not previous_state:
            first_rule = rules[0]
            return (
                first_rule.state,
                first_rule.group_id.id,
            )

        # Find current stage
        current_rule = rules.filtered(lambda r: r.state == previous_state)
        if not current_rule:
            # Fallback → restart from first stage
            first_rule = rules[0]
            return (
                first_rule.state,
                first_rule.group_id.id,
            )

        current_rule = current_rule[0]
        next_rules = rules.filtered(
            lambda r: r.sequence > current_rule.sequence
        )

        # Last stage → stay there
        if not next_rules:
            return (
                current_rule.state,
                current_rule.group_id.id,
            )

        next_rule = next_rules[0]
        return (
            next_rule.state,
            next_rule.group_id.id,
        )


