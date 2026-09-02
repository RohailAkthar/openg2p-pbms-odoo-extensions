from odoo import models, fields

from .registry import G2PRegistry


class G2PRegisterHousehold(models.Model):
    _name = "g2p.register.household"
    _description = "Nigeria NSR Household Registry"
    _table = "g2p_register_households"
    _inherit = "g2p.registry"

    # Core Identifiers & Links
    functional_record_id = fields.Char(string="Functional Record ID")
    link_internal_record_id = fields.Char(string="Link Internal Record ID")
    link_foundational_id = fields.Char(string="Link Foundational ID")
    record_name = fields.Char(string="Record Name")
    record_image_document_id = fields.Text(string="Record Image Document ID")
    search_text = fields.Text(string="Search Text")
    record_status = fields.Selection(
        selection=[
            ("ACTIVE", "Active"),
            ("INACTIVE", "Inactive"),
            ("ARCHIVED", "Archived"),
        ],
        string="Record Status",
        default="ACTIVE",
    )
    record_status_reason = fields.Char(string="Record Status Reason")

    # Geographic & Location Fields
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    altitude = fields.Char(string="Altitude")
    plus_code = fields.Char(string="Plus Code")
    address_line_1 = fields.Char(string="Address Line 1 / Community")
    address_line_2 = fields.Char(string="Address Line 2")
    postal_code = fields.Char(string="Postal Code")
    country_code = fields.Char(string="Country Code")
    geo_lowest_level_value_id = fields.Char(string="Geo Location / Ward Code")
    geo_code_hierarchy_json = fields.Char(string="Geo Hierarchy (JSON)")

    # Household Headship
    household_head_internal_record_id = fields.Char(string="Household Head Internal ID")
    household_head_name = fields.Char(string="Household Head Name")
    headship_type = fields.Selection(
        selection=[
            ("MALE_HEADED", "Male Headed"),
            ("FEMALE_HEADED", "Female Headed"),
            ("CHILD_HEADED", "Child Headed"),
            ("ELDERLY_HEADED", "Elderly Headed"),
            ("DISABLED_HEADED", "Disabled Headed"),
        ],
        string="Headship Type",
    )
    husband_dead = fields.Boolean(string="Husband Deceased", default=False)
    husband_dead_date = fields.Date(string="Husband Deceased Date")

    # Household Demographics & Composition
    size_total = fields.Integer(string="Total Household Size")
    size_adults = fields.Integer(string="Adult Members Count")
    size_children_u5 = fields.Integer(string="Children Under 5 Count")
    size_school_age = fields.Integer(string="School-Age Children Count")
    size_elderly = fields.Integer(string="Elderly Members Count")
    number_of_female_members = fields.Integer(string="Number of Female Members")
    number_of_male_members = fields.Integer(string="Number of Male Members")
    elderly_member_present = fields.Boolean(string="Elderly Member Present")

    # Dwelling & Living Conditions
    dwelling_type = fields.Selection(
        selection=[
            ("PERMANENT", "Permanent"),
            ("SEMI_PERMANENT", "Semi-Permanent"),
            ("TEMPORARY", "Temporary"),
        ],
        string="Dwelling Type",
    )
    roof_material = fields.Selection(
        selection=[
            ("THATCH", "Thatch / Leaves"),
            ("CORRUGATED_IRON", "Corrugated Iron / Metal Sheets"),
            ("CONCRETE", "Concrete / Cement"),
            ("TILE", "Roofing Tiles"),
            ("PLASTIC_SHEET", "Plastic Sheet / Tarpaulin"),
            ("OTHER", "Other"),
        ],
        string="Roof Material",
    )
    wall_material = fields.Selection(
        selection=[
            ("MUD", "Mud / Earth"),
            ("WOOD", "Wood / Planks"),
            ("BAMBOO", "Bamboo / Reeds"),
            ("STONE", "Stone"),
            ("BRICK", "Burnt Bricks"),
            ("CONCRETE", "Concrete Blocks"),
            ("OTHER", "Other"),
        ],
        string="Wall Material",
    )
    floor_material = fields.Selection(
        selection=[
            ("EARTH", "Earth / Sand / Dirt"),
            ("WOOD", "Wood Planks"),
            ("CEMENT", "Cement / Concrete Screed"),
            ("TILE", "Ceramic / Vinyl Tiles"),
            ("OTHER", "Other"),
        ],
        string="Floor Material",
    )
    tenure_status = fields.Selection(
        selection=[
            ("OWNED", "Owner / Occupied"),
            ("RENTED", "Rented"),
            ("HOSTED", "Hosted / Provided Rent-Free"),
            ("TEMPORARY", "Temporary Shelter / Squatting"),
        ],
        string="Tenure Status",
    )
    rooms_count = fields.Integer(string="Number of Rooms")
    overcrowding_indicator = fields.Float(string="Overcrowding Indicator")

    # WASH & Energy Utilities
    water_source_type = fields.Selection(
        selection=[
            ("PIPED", "Piped Water Connection"),
            ("PUBLIC_TAP", "Public Tap / Standpipe"),
            ("WELL", "Protected Well / Borehole"),
            ("SPRING", "Protected Spring"),
            ("SURFACE_WATER", "River / Stream / Dam / Lake"),
            ("RAINWATER", "Rainwater Collection"),
            ("TANKER_TRUCK", "Tanker Truck / Cart Vendor"),
            ("OTHER", "Other"),
        ],
        string="Water Source",
    )
    water_distance_minutes = fields.Integer(string="Water Fetch Distance (Minutes)")
    sanitation_type = fields.Selection(
        selection=[
            ("FLUSH_TOILET", "Flush / Pour-Flush Toilet"),
            ("PIT_LATRINE", "Ventilated Improved Pit Latrine"),
            ("COMPOSTING_TOILET", "Composting Toilet"),
            ("SHARED", "Shared / Public Facility"),
            ("OPEN", "Open Defecation / Bush / Field"),
            ("OTHER", "Other"),
        ],
        string="Sanitation Facility",
    )
    lighting_source = fields.Selection(
        selection=[
            ("GRID", "National Electricity Grid"),
            ("SOLAR", "Solar System / Home Unit"),
            ("GENERATOR", "Fuel Generator"),
            ("KEROSENE", "Kerosene Lantern"),
            ("CANDLE", "Candles / Torches"),
            ("NONE", "None"),
        ],
        string="Main Lighting Source",
    )
    cooking_fuel_type = fields.Selection(
        selection=[
            ("ELECTRICITY", "Electricity"),
            ("GAS", "LPG / Natural Gas"),
            ("KEROSENE", "Kerosene Stove"),
            ("CHARCOAL", "Charcoal"),
            ("FIREWOOD", "Firewood"),
            ("BIOMASS", "Agricultural Biomass / Dung"),
            ("OTHER", "Other"),
        ],
        string="Main Cooking Fuel",
    )
    mobile_phone_type = fields.Selection(
        selection=[
            ("NONE", "No Phone"),
            ("BASIC", "Basic / Feature Phone"),
            ("SMARTPHONE", "Smartphone"),
        ],
        string="Mobile Phone Ownership",
    )
