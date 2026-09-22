from odoo import fields, models


class G2PEntitlementRuleDefinitionExtend(models.Model):
    """
    Extension of G2PEntitlementRuleDefinition to make pbms_domain optional.
    The domain widget is not shown in the entitlement rule form view for the
    Gramstack Household registry, so the field must not be mandatory.
    An empty domain '[]' means no filter (all records match).
    """
    _name = "g2p.entitlement.rule.definition"
    _inherit = "g2p.entitlement.rule.definition"

    pbms_domain = fields.Char(
        string="Domain",
        required=False,
        default="[]",
    )


class G2PPriorityRuleDefinitionExtend(models.Model):
    """
    Extension of G2PPriorityRuleDefinition to make pbms_domain optional.
    The domain widget is not shown in the priority rule form view for the
    Gramstack Household registry, so the field must not be mandatory.
    An empty domain '[]' means no filter (all records match).
    """
    _name = "g2p.priority.rule.definition"
    _inherit = "g2p.priority.rule.definition"

    pbms_domain = fields.Char(
        string="Domain",
        required=False,
        default="[]",
    )
