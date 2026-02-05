from odoo import models, fields


class G2PProgramDefinition(models.Model):
    _inherit = "g2p.program.definition"

    disbursement_verification_ids = fields.One2many(
        "g2p.disbursement.verification.rule.definition",
        "program_id",
        string="Disbursement Verification Rules",
    )
