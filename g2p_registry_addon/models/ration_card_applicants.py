from odoo import models, fields, api

from .registry import G2PRegistry


class G2PRegistryRationCardApplicants(models.Model):
    """Ration Card Applicant Registry Model"""
    _name = 'g2p.registry.ration.card.applicants'
    _description = 'Ration Card Applicant Registry'
    _inherit = 'g2p.registry'

    ration_card_application_id = fields.Char(
        string='Ration Card Application ID',
        help='Unique identifier for the ration card application'
    )
    individual_registry_id = fields.Integer(
        string='Individual Registry ID',
        help='Registry ID of the individual applicant'
    )
    individual_unique_id = fields.Char(
        string='Individual Unique ID',
        help='MOSIP generated unique ID for the individual applicant'
    )
    aadhaar_id = fields.Char(
        string='Applicant Aadhaar',
        help='Aadhaar number of the applicant'
    )
    family_unique_id = fields.Char(
        string='Family Unique ID',
        help='MOSIP generated unique ID for the family'
    )
    family_registry_id = fields.Integer(
        string='Family Registry ID',
        help='Registry ID of the family'
    )
    application_date = fields.Date(
        string='Application Date',
        help='Date of ration card application'
    )
    verified_by = fields.Char(
        string='Verified By',
        help='Name or identifier of the person who verified the application'
    )
    verification_time_stamp = fields.Datetime(
        string='Verification Time Stamp',
        help='Date and time when the application was verified'
    )
    application_channel = fields.Char(
        string='Application Channel',
        help='Channel through which the application was submitted'
    )