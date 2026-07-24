from odoo import models, fields, api

from .registry import G2PRegistry


class G2PHouseholdRegistry(models.Model):
    _name = "g2p.household.registry"
    _description = "Household Registry"
    _inherit = "g2p.registry"

    name = fields.Char(string="Household Name", required=True)
    household_id = fields.Char(string="Household ID")
    household_size = fields.Integer(string="Household Size")
    head_name = fields.Char(string="Head Name")
    head_gender = fields.Selection(
        selection=[("male", "Male"), ("female", "Female")], string="Head Gender"
    )
    head_phone = fields.Char(string="Head Phone")
    head_dob = fields.Date(string="Head Date of Birth")
    children_count = fields.Integer(string="Children Count")
    adult_count = fields.Integer(string="Adult Count")
    has_pregnant_member = fields.Selection(
        selection=[("yes", "Yes"), ("no", "No")], string="Has Pregnant Member"
    )
    has_disabled_member = fields.Selection(
        selection=[("yes", "Yes"), ("no", "No")], string="Has Disabled Member"
    )
    large_area_id = fields.Integer(string="Large Area ID")
    large_area_code = fields.Char(string="Large Area Code")
    small_area_id = fields.Integer(string="Small Area ID")
    small_area_code = fields.Char(string="Small Area Code")
