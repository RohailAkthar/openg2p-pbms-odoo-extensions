from odoo import models, fields
from .registry import G2PRegistry


class G2PGramstackHouseholdRegistry(models.Model):
    _name = "g2p.gramstack.household.registry"
    _description = "GramStack Household Registry"
    _inherit = "g2p.registry"
    _table = "g2p_register_gramstack_households"

    # Core Household Attributes
    household_reference_name = fields.Char(string="Household Reference Name")
    house_reference_no = fields.Char(string="House Reference No")
    lokos_id = fields.Char(string="LokOS ID")
    village = fields.Char(string="Village")
    gram_panchayat = fields.Char(string="Gram Panchayat")
    block = fields.Char(string="Block")
    district = fields.Char(string="District")
    pds_classification = fields.Char(string="PDS Classification")

    # SHGlokos Denormalized Attributes
    aadhaar_number = fields.Char(string="Aadhaar Number")
    member_id = fields.Char(string="SHG Member ID")
    shg_id = fields.Char(string="SHG ID")
    shg_name = fields.Char(string="SHG Name")
    vo_id = fields.Char(string="VO ID")
    vo_name = fields.Char(string="VO Name")
    clf_id = fields.Char(string="CLF ID")
    clf_name = fields.Char(string="CLF Name")
    member_name = fields.Char(string="SHG Member Name")
    gender = fields.Char(string="Gender")
    dob = fields.Date(string="Date of Birth")
    relationship_to_hoh = fields.Char(string="Relationship to HOH")
    mobile_number = fields.Char(string="Mobile Number")
    bank_account_no = fields.Char(string="Bank Account Number")
    ifsc = fields.Char(string="IFSC Code")
    shg_join_date = fields.Date(string="SHG Join Date")
    shg_role = fields.Char(string="SHG Role")
    monthly_savings_amount = fields.Float(string="Monthly Savings (₹)")
    internal_loan_outstanding = fields.Float(string="Internal Loan Outstanding (₹)")
    ccl_limit = fields.Float(string="CCL Limit (₹)")
    ccl_utilized = fields.Float(string="CCL Utilized (₹)")
    shg_grading = fields.Char(string="SHG Grading")

    # Scheme Application & Tranche Lifecycle Attributes
    scheme_code = fields.Char(string="Scheme Code")
    scheme_name = fields.Char(string="Scheme Name")
    applicant_name = fields.Char(string="Applicant Name")
    status = fields.Char(string="Application / Tranche Status")
    applied_at = fields.Datetime(string="Applied At")
