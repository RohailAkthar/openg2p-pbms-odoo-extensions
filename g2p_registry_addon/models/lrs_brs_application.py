from odoo import models, fields, api

from .registry import G2PRegistry


class G2PRegistryLrsBrsApplication(models.Model):
    """LRS BRS Application Registry Model"""
    _name = 'g2p.registry.lrs.brs.application'
    _description = 'LRS BRS Application Registry'
    _inherit = 'g2p.registry'

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

    lrs_brs_application_id = fields.Char(
        string='LRS BRS Application ID',
        help='Unique identifier for the LRS BRS application'
    )
    
    # Scheme information
    scheme = fields.Char(
        string='Scheme',
        help='Name of the scheme applied for'
    )
