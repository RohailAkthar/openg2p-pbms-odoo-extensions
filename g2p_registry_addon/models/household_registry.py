from odoo import models, fields

from .registry import G2PRegistry


class G2PHouseholdRegistry(models.Model):
    _name = "g2p.household.registry"
    _description = "Household Registry"
    _inherit = "g2p.registry"
    _table = "g2p_register_households"

    # Head of Household Details
    household_head_name = fields.Char(string="Head of Household Name")
    household_head_internal_record_id = fields.Char(string="Head Internal Record ID")
    headship_type = fields.Char(string="Headship Type")
    husband_dead = fields.Boolean(string="Husband Deceased")

    # Family Structure & Size
    size_total = fields.Integer(string="Total Household Size")
    size_adults = fields.Integer(string="Adults Count")
    size_children_u5 = fields.Integer(string="Children Under 5")
    size_school_age = fields.Integer(string="School-Age Children")
    size_elderly = fields.Integer(string="Elderly Members")
    number_of_female_members = fields.Integer(string="Female Members Count")
    number_of_male_members = fields.Integer(string="Male Members Count")

    # Housing & Living Conditions
    dwelling_type = fields.Char(string="Dwelling Type")
    roof_material = fields.Char(string="Roof Material")
    wall_material = fields.Char(string="Wall Material")
    floor_material = fields.Char(string="Floor Material")
    tenure_status = fields.Char(string="Tenure Status")
    rooms_count = fields.Integer(string="Rooms Count")

    # Utilities & Water Access
    water_source_type = fields.Char(string="Water Source Type")
    sanitation_type = fields.Char(string="Sanitation Type")
    lighting_source = fields.Char(string="Lighting Source")
    cooking_fuel_type = fields.Char(string="Cooking Fuel Type")

    # PDS Food Security (Ration Card)
    ration_card_number = fields.Char(string="Ration Card Number")
    ration_card_type = fields.Char(string="Ration Card Type")
    fps_shop_code = fields.Char(string="FPS Shop Code")
    dealer_name = fields.Char(string="Dealer Name")
    monthly_entitlement_kg = fields.Float(string="Monthly Entitlement (KG)")

    # Geographic Location
    district = fields.Char(string="District")
    block = fields.Char(string="Block")
    village = fields.Char(string="Village")
