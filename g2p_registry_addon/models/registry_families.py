from odoo import models, fields, api

from .registry import G2PRegistry


class G2PRegistryFamilies(models.Model):
    """Family Registry Model"""
    _name = 'g2p.registry.families'
    _description = 'Family Registry'
    _inherit = 'g2p.registry'

    family_unique_id = fields.Char(
        string='Family Unique ID',
        help='MOSIP generated unique ID for family'
    )
    hof_individual_registry_id = fields.Integer(
        string='HOF Individual Registry ID',
        help='Registry ID of the Head of Family (HOF) individual'
    )
    hof_individual_unique_id = fields.Char(
        string='HOF Individual Unique ID',
        help='MOSIP generated unique ID for the Head of Family (HOF)'
    )
    hof_individual_name = fields.Char(
        string='HOF Individual Name',
        help='Name of the Head of Family (HOF)'
    )