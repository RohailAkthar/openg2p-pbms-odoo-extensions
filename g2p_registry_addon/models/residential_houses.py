from odoo import models, fields, api

from .registry import G2PRegistry


class G2PResidentialHouses(models.Model):
    _name = "g2p.registry.residential.houses"
    _description = "Residential Houses Registry"
    _inherit = "g2p.registry"


    individual_registry_id = fields.Integer(
        string='Individual Registry ID',
        help='Reference to individual registry record'
    )
    individual_unique_id = fields.Char(
        string='Individual Unique ID',
        help='MOSIP generated unique ID for individual'
    )
    aadhaar_id = fields.Char(
        string='Applicant Aadhaar',
        help='Aadhaar number of the applicant'
    )
    family_unique_id = fields.Char(
        string='Family Unique ID',
        help='MOSIP generated unique ID for family'
    )
    family_registry_id = fields.Integer(
        string='Family Registry ID',
        help='Reference to family registry record'
    )
    property_id_tax_records = fields.Char(
        string='Property Tax Records',
        help='Tax records for the property'
    )
    built_up_area_in_sq_feet = fields.Float(
        string='Built-up Area (in Sq. Feet)',
        help='Total built-up area of the residential house in square feet'
    )