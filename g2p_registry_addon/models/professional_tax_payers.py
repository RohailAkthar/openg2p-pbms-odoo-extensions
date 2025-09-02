from odoo import models, fields, api

from .registry import G2PRegistry


class G2PRegistryProfessionalTaxPayers(models.Model):
    """Professional Tax Registry Model"""
    _name = 'g2p.registry.professional.tax.payers'
    _description = 'Professional Tax Registry'
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

    professional_tax_payer_id = fields.Char(
        string='Professional Tax Payer ID',
        help='Unique identifier for the professional tax payer'
    )

    # Business type
    type_of_business = fields.Char(
        string='Type of Business',
        help='Category or type of business for professional tax'
    )