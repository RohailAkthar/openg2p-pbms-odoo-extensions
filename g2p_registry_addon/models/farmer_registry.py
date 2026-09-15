from odoo import models, fields

from .registry import G2PRegistry


class G2PFarmerRegistry(models.Model):
    _name = "g2p.farmer.registry"
    _description = "Farmer Registry"
    _inherit = "g2p.registry"
    _table = "g2p_register_farmers"

    # Farmer Identification
    farmer_id = fields.Char(string="Farmer ID")
    farmer_name = fields.Char(string="Farmer Name", required=True)
    relation_name = fields.Char(string="Relation Name")
    farmer_mobile_number = fields.Char(string="Farmer Mobile Number")
    gender = fields.Selection(
        selection=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        string="Gender",
    )

    # Land & Agriculture
    land_area_acres = fields.Float(string="Land Area (Acres)")
    land_ownership_type = fields.Char(string="Land Ownership Type")
    crop_type = fields.Char(string="Crop Type")
    khata_number = fields.Char(string="Khata Number")
    khesra_number = fields.Char(string="Khesra Number")
    khatiyan_number = fields.Char(string="Khatiyan Number")

    # Government Schemes
    pm_kisan_enrolled = fields.Boolean(string="PM-KISAN Enrolled")
    pmfby_enrolled = fields.Boolean(string="PMFBY Enrolled")

    # Livestock & Income
    no_of_cattle_heads = fields.Integer(string="No of Cattle Heads")
    no_of_poultry_heads = fields.Integer(string="No of Poultry Heads")
    annual_income = fields.Float(string="Annual Income")

    # Banking & Financials
    farmer_bank_account_no = fields.Char(string="Bank Account Number")
    bank_name = fields.Char(string="Bank Name")
    ifsc_code = fields.Char(string="IFSC Code")

    # Geographic Location
    district = fields.Char(string="District")
    block = fields.Char(string="Block")
    village = fields.Char(string="Village")

    # Link identifier
    link_registry_id = fields.Char(string="Link Registry ID")
