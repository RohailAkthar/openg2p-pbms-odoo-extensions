from odoo import models, fields

from .registry import G2PRegistry


class G2PGroupRegistry(models.Model):
    _name = "g2p.group.registry"
    _description = "Group Registry"
    _inherit = "g2p.registry"
    _table = "g2p_register_groups"

    # Group Identification & Hierarchy
    group_name = fields.Char(string="Group Name", required=True)
    group_type = fields.Char(string="Group Type")
    shg_id = fields.Char(string="SHG ID")
    shg_code = fields.Char(string="SHG Code")
    lokos_id = fields.Char(string="LokOS ID")
    vo_name = fields.Char(string="VO Name")
    clf_name = fields.Char(string="CLF Name")

    # Key Representative / Office Bearer
    member_id = fields.Char(string="Key Member ID")
    key_member_name = fields.Char(string="Key Member Name")
    key_member_role = fields.Char(string="Key Member Role")
    key_member_mobile = fields.Char(string="Key Member Mobile")

    # Banking & Financials
    bank_name = fields.Char(string="Bank Name")
    bank_account_no = fields.Char(string="Bank Account Number")
    ifsc_code = fields.Char(string="IFSC Code")
    monthly_savings_amount = fields.Float(string="Monthly Savings Amount")
    internal_loan_outstanding = fields.Float(string="Internal Loan Outstanding")
    ccl_limit = fields.Float(string="Cash Credit Limit (CCL)")
    ccl_utilised = fields.Float(string="CCL Utilised")

    # Governance & Operational
    shg_grading = fields.Char(string="SHG Grading")
    formation_date = fields.Date(string="Formation Date")
    meeting_frequency = fields.Char(string="Meeting Frequency")

    # Geographic Location
    district = fields.Char(string="District")
    block = fields.Char(string="Block")
    gram_panchayat = fields.Char(string="Gram Panchayat")
    village = fields.Char(string="Village")
    pin_code = fields.Char(string="PIN Code")
