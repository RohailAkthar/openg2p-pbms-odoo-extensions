from odoo import fields, models


class NsipaEntitlementDefaults(models.Model):
    _inherit = "g2p.entitlement.rule.definition"

    # The Domain widget is hidden in the entitlement rule dialog (views/mnemonic_labels.xml), but the column is
    # required, so new rules need a value: "[]" means "match all records" (every eligible beneficiary).
    pbms_domain = fields.Char(default="[]")
