from odoo import models, fields

from .registry import G2PRegistry


class G2PIndividualRegistry(models.Model):
    _name = "g2p.individual.registry"
    _description = "Individual Registry"
    _inherit = "g2p.registry"
    _table = "g2p_register_individuals"

    # Demographics
    full_name = fields.Char(string="Full Name", required=True)
    gender = fields.Selection(
        selection=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender",
    )
    estimated_age = fields.Integer(string="Estimated Age")
    dob = fields.Char(string="Date of Birth")
    citizenship_category = fields.Char(string="Citizenship Category")
    residency_status = fields.Char(string="Residency Status")

    # Geographic Location
    district = fields.Char(string="District")
    block = fields.Char(string="Block")
    village = fields.Char(string="Village")
    gp = fields.Char(string="Gram Panchayat")

    # Identifiers & Banking
    aadhaar_number = fields.Char(string="Aadhaar Number")
    mobile_number = fields.Char(string="Mobile Number")
    bank_account_no = fields.Char(string="Bank Account Number")
    ifsc = fields.Char(string="IFSC Code")

    # Vulnerability & Social Status
    primary_livelihood = fields.Char(string="Primary Livelihood")
    disability_status = fields.Char(string="Disability Status")
    plw_status = fields.Boolean(string="Pregnant / Lactating Woman")
    orphanhood_flag = fields.Boolean(string="Orphanhood")
    chronic_illness_flag = fields.Boolean(string="Chronic Illness")

    # Cross-Registry Identifiers (Federated NSR)
    household_id = fields.Char(string="Household ID")
    farmer_id = fields.Char(string="Farmer ID")
    pm_kisan_enrolled = fields.Boolean(string="PM-KISAN Enrolled")
    pmfby_enrolled = fields.Boolean(string="PMFBY Enrolled")
    ration_card_number = fields.Char(string="Ration Card Number")
    ration_card_type = fields.Char(string="Ration Card Type")
    member_id = fields.Char(string="SHG Member ID")
    shg_name = fields.Char(string="SHG Name")
    student_id = fields.Char(string="Student ID")
