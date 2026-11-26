from odoo import fields, models

# Presentation only: every "... Mnemonic" field label shown to end users is now "... Name".
# Only the label (string) is redeclared; Odoo merges it into the existing field, so type, related,
# required, compute etc. are unchanged. Generated from the field list; see views/mnemonic_labels.xml for
# labels that are hard-coded in views and reports.

class NsipaNameLabels0(models.Model):
    _inherit = "g2p.administrative.area.large"
    area_mnemonic = fields.Char(string="Area Name")

class NsipaNameLabels1(models.Model):
    _inherit = "g2p.administrative.area.small"
    administrative_area_large_mnemonic = fields.Char(string="Large Area Name")
    area_mnemonic = fields.Char(string="Area Name")

class NsipaNameLabels2(models.Model):
    _inherit = "g2p.agency"
    agency_mnemonic = fields.Char(string="Agency Name")

class NsipaNameLabels3(models.Model):
    _inherit = "g2p.agency.program.benefit.codes"
    agency_mnemonic = fields.Char(string="Agency Name")
    benefit_mnemonic = fields.Char(string="Transfer Name")
    program_mnemonic = fields.Char(string="Program Name")

class NsipaNameLabels4(models.TransientModel):
    _inherit = "g2p.api.disbursement.batch.line"
    benefit_code_mnemonic = fields.Char(string="Transfer Name")

class NsipaNameLabels5(models.TransientModel):
    _inherit = "g2p.api.disbursement.envelope.line"
    benefit_code_mnemonic = fields.Char(string="Transfer Name")
    benefit_program_mnemonic = fields.Char(string="Program Name")
    cycle_code_mnemonic = fields.Char(string="Cycle Name")

class NsipaNameLabels6(models.Model):
    _inherit = "g2p.beneficiary.list"
    mnemonic = fields.Char(string="Name")

class NsipaNameLabels7(models.Model):
    _inherit = "g2p.benefit.codes"
    benefit_mnemonic = fields.Char(string="Transfer Name")

class NsipaNameLabels8(models.TransientModel):
    _inherit = "g2p.bgtask.summary.wizard"
    mnemonic = fields.Char(string="Name")

class NsipaNameLabels9(models.TransientModel):
    _inherit = "g2p.disbursement.batch.summary.geo"
    administrative_zone_mnemonic_large = fields.Char(string="Large Zone Name")
    administrative_zone_mnemonic_small = fields.Char(string="Small Zone Name")
    agency_mnemonic = fields.Char(string="Agency Name")
    warehouse_mnemonic = fields.Char(string="Warehouse Name")

class NsipaNameLabels10(models.TransientModel):
    _inherit = "g2p.disbursement.batch.summary.wizard"
    benefit_code_mnemonic = fields.Char(string="Transfer Name")
    disbursement_cycle_code_mnemonic = fields.Char(string="Disbursement Cycle Name")

class NsipaNameLabels11(models.Model):
    _inherit = "g2p.disbursement.cycle"
    cycle_mnemonic = fields.Char(string="Cycle Name")

class NsipaNameLabels12(models.TransientModel):
    _inherit = "g2p.disbursement.envelope.summary.geo"
    administrative_zone_mnemonic_large = fields.Char(string="Large Zone Name")
    administrative_zone_mnemonic_small = fields.Char(string="Small Zone Name")
    agency_mnemonic = fields.Char(string="Agency Name")
    warehouse_mnemonic = fields.Char(string="Warehouse Name")

class NsipaNameLabels13(models.TransientModel):
    _inherit = "g2p.disbursement.envelope.summary.wizard"
    benefit_code_mnemonic = fields.Char(string="Transfer Name")

class NsipaNameLabels14(models.Model):
    _inherit = "g2p.eligibility.rule.definition"
    mnemonic = fields.Char(string="Rule Name")

class NsipaNameLabels15(models.Model):
    _inherit = "g2p.enrollment.cycle"
    cycle_mnemonic = fields.Char(string="Enrollment Cycle Name")

class NsipaNameLabels16(models.Model):
    _inherit = "g2p.entitlement.rule.definition"
    mnemonic = fields.Char(string="Rule Name")

class NsipaNameLabels17(models.Model):
    _inherit = "g2p.priority.rule.definition"
    mnemonic = fields.Char(string="Rule Name")

class NsipaNameLabels18(models.Model):
    _inherit = "g2p.program.benefit.codes"
    benefit_mnemonic = fields.Char(string="Transfer Name")

class NsipaNameLabels19(models.Model):
    _inherit = "g2p.program.definition"
    program_mnemonic = fields.Char(string="Program Name")

class NsipaNameLabels20(models.Model):
    _inherit = "g2p.warehouse"
    warehouse_mnemonic = fields.Char(string="Warehouse Name")

class NsipaNameLabels21(models.Model):
    _inherit = "g2p.warehouse.program.benefit.codes"
    benefit_mnemonic = fields.Char(string="Transfer Name")
    program_mnemonic = fields.Char(string="Program Name")
    warehouse_mnemonic = fields.Char(string="Warehouse Name")
