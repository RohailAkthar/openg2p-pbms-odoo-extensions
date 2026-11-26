from odoo import fields, models

# Presentation only: "Benefit Code" wording shown to end users is now "Transfer Type" / "Transfer".
# Only the label (string) is redeclared; Odoo merges it into the existing field (type, related, comodel,
# selection values, domains etc. are unchanged).

class NsipaTransferLabels0(models.Model):
    _inherit = "g2p.benefit.codes"
    benefit_type = fields.Selection(string="Transfer Type")
    benefit_description = fields.Text(string="Transfer Description")
    measurement_unit = fields.Char(string="Currency")

class NsipaTransferLabels1(models.Model):
    _inherit = "g2p.program.benefit.codes"
    benefit_type = fields.Selection(string="Transfer Type")
    benefit_description = fields.Text(string="Transfer Description")
    measurement_unit = fields.Char(string="Currency")
    benefit_code_id = fields.Many2one(string="Transfer")

class NsipaTransferLabels2(models.Model):
    _inherit = "g2p.agency.program.benefit.codes"
    benefit_type = fields.Selection(string="Transfer Type")
    benefit_description = fields.Text(string="Transfer Description")
    measurement_unit = fields.Char(string="Currency")
    benefit_code_id = fields.Many2one(string="Transfer")
    benefit_codes = fields.Many2many(string="Transfers")

class NsipaTransferLabels3(models.Model):
    _inherit = "g2p.warehouse.program.benefit.codes"
    benefit_type = fields.Selection(string="Transfer Type")
    benefit_description = fields.Text(string="Transfer Description")
    measurement_unit = fields.Char(string="Currency")
    benefit_code_id = fields.Many2one(string="Transfer")
    benefit_codes = fields.Many2many(string="Transfers")

class NsipaTransferLabels4(models.Model):
    _inherit = "g2p.entitlement.rule.definition"
    measurement_unit = fields.Char(string="Currency")
    benefit_code_id = fields.Many2one(string="Transfer")
    allowed_benefit_code_ids = fields.Many2many(string="Transfers")

class NsipaTransferLabels5(models.Model):
    _inherit = "g2p.program.definition"
    benefit_code_ids = fields.Many2many(string="Transfers")
    program_benefit_code_ids = fields.One2many(string="Program Transfer Types")

class NsipaTransferLabels6(models.Model):
    _inherit = "g2p.agency"
    agency_program_benefit_codes = fields.One2many(string="Agency Program Transfer Types")

class NsipaTransferLabels7(models.Model):
    _inherit = "g2p.warehouse"
    warehouse_program_benefit_codes = fields.One2many(string="Warehouse Program Transfer Types")
