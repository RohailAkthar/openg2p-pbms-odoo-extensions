from odoo import models, fields

from .registry import G2PRegistry


class G2PFarmerRegistry(models.Model):
    _name = "g2p.farmer.registry"
    _description = "Farmer Registry"
    _inherit = "g2p.registry"
    _table = "g2p_register_farmers"
    _rec_name = "farmer_name"

    # Farmer Identification
    record_name = fields.Char(string="Record Name")
    functional_record_id = fields.Char(string="System ID")
    farmer_id = fields.Char(string="AgriStack Farmer ID")
    foundational_id = fields.Char(string="Aadhaar Number")
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")
    farmer_name = fields.Char(string="Farmer Name")
    relation_name = fields.Char(string="Father / Relative Name")
    farmer_mobile_number = fields.Char(string="Farmer Mobile Number")
    mobile_phone_number = fields.Char(string="Mobile Phone Number")
    gender = fields.Selection(
        selection=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Gender",
    )
    birth_date = fields.Date(string="Date of Birth")

    # Land & Agriculture
    land_area_acres = fields.Float(string="Operated Land Area (Acres)")
    land_ownership_type = fields.Char(string="Ownership Type")
    crop_type = fields.Char(string="Standing Crops / Crop Type")
    khata_number = fields.Char(string="Khata Number")
    khesra_number = fields.Char(string="Khesra Number")
    khatiyan_number = fields.Char(string="Khatiyan Number")

    # Government Schemes
    pm_kisan_enrolled = fields.Boolean(string="PM-KISAN Enrolled")
    pmfby_enrolled = fields.Boolean(string="PMFBY Enrolled")

    # Banking & Financials
    farmer_bank_account_no = fields.Char(string="DBT Bank Account")
    bank_name = fields.Char(string="Bank Name")
    ifsc_code = fields.Char(string="IFSC Code")

    # Geographic Location
    district = fields.Char(string="District")
    block = fields.Char(string="Block / Anchal")
    village = fields.Char(string="Village / Mauza")
