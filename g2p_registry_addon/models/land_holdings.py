from odoo import models, fields, api

from .registry import G2PRegistry


class G2PLandHoldings(models.Model):
    _name = "g2p.registry.land.holdings"
    _description = "Land Holdings Registry"
    _inherit = "g2p.registry"

    id = fields.Integer(
        string='ID',
        help='Primary key identifier for the land holding record'
    )
    ration_card_application_id = fields.Char(
        string='Ration Card Application ID',
        help='Unique identifier for the ration card application'
    )
    individual_registry_id = fields.Integer(
        string='Individual Registry ID',
        help='Reference to individual registry record'
    )
    individual_unique_id = fields.Char(
        string='Individual Unique ID',
        help='MOSIP generated unique ID for individual'
    )
    applicant_aadhaar = fields.Char(
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
    land_area_in_acres = fields.Float(
        string='Land Area (in Acres)',
        help='Total land area held in acres'
    )