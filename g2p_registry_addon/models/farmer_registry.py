from odoo import models, fields, api

from .registry import G2PRegistry


class G2PFarmerRegistry(models.Model):
    _name = "g2p.farmer.registry"
    _description = "Farmer Registry"
    _inherit = "g2p.registry"

    name = fields.Char(string="Name", required=True)
    gender = fields.Selection(
        selection=[("male", "Male"), ("female", "Female")], string="Gender"
    )
    land_area = fields.Float(string="Land Area")
    no_of_cattle_heads = fields.Integer(string="No of Cattle Heads")
    no_of_poultry_heads = fields.Integer(string="No of Poultry Heads")
    annual_income = fields.Float(string="Annual Income")
    large_area_id = fields.Integer(string="Large Area ID")
    large_area_code = fields.Char(string="Large Area Code")
    small_area_id = fields.Integer(string="Small Area ID")
    small_area_code = fields.Char(string="Small Area Code")
