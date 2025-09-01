from odoo import models, fields, api

from .registry import G2PRegistry


class G2PRegistryIndividuals(models.Model):
    """Individual Registry Model"""
    _name = 'g2p.registry.individuals'
    _description = 'Individual Registry'
    _inherit = 'g2p.registry'

    id = fields.Integer(
        string='ID',
        help='Primary key identifier for the individual record'
    )
    individual_unique_id = fields.Char(
        string='Individual Unique ID',
        help='MOSIP generated unique ID for individual'
    )
    owner_aadhaar = fields.Char(
        string='Owner Aadhaar',
        help='Aadhaar number of the individual'
    )
    family_unique_id = fields.Char(
        string='Family Unique ID',
        help='MOSIP generated unique ID for family'
    )
    family_registry_id = fields.Integer(
        string='Family Registry ID',
        help='Reference to family registry record'
    )
    ration_card_id = fields.Char(
        string='Ration Card ID',
        help='Ration card identifier'
    )
    praja_palana_id = fields.Char(
        string='Praja Palana ID',
        help='Praja Palana identifier'
    )
    icdb_id = fields.Char(
        string='ICDB ID',
        help='ICDB identifier'
    )
    name = fields.Char(
        string='Name',
        help='Full name of the individual'
    )
    family_name = fields.Char(
        string='Family Name',
        help='Family name of the individual'
    )
    given_name = fields.Char(
        string='Given Name',
        help='Given name of the individual'
    )
    gender = fields.Char(
        string='Gender',
        help='Gender of the individual'
    )
    village = fields.Char(
        string='Village',
        help='Village of residence'
    )
    mandal_string = fields.Char(
        string='Mandal',
        help='Mandal of residence'
    )
    district_string = fields.Char(
        string='District',
        help='District of residence'
    )
    address = fields.Text(
        string='Address',
        help='Full address of the individual'
    )
