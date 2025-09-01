from odoo import models, fields, api


class G2PRegistryFamilies(models.Model):
    """Family Registry Model"""
    _name = 'g2p.registry.families'
    _description = 'Family Registry'
    _inherit = 'g2p.registry'

    id = fields.Integer(
        string='ID',
        help='Primary key identifier for the family record'
    )
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