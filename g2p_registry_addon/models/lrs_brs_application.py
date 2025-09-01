from odoo import models, fields, api


class G2PRegistryLrsBrsApplication(models.Model):
    """LRS BRS Application Registry Model"""
    _name = 'g2p.registry.lrs.brs.application'
    _description = 'LRS BRS Application Registry'
    _inherit = 'g2p.registry'
    
    id = fields.Integer(
        string='ID',
        help='Primary key identifier for the LRS BRS application record'
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
    
    # Scheme information
    scheme = fields.Char(
        string='Scheme',
        help='Name of the scheme applied for'
    )
