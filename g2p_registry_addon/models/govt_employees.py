from odoo import models, fields, api

from .registry import G2PRegistry


class G2PRegistryGovtEmployees(models.Model):
    """Government Employee Status Registry Model"""
    _name = 'g2p.registry.govt.employees'
    _description = 'Government Employees Registry'
    _inherit = 'g2p.registry'

    individual_registry_id = fields.Integer(
        string='Individual Registry ID',
        help='Reference to individual registry record'
    )
    individual_unique_id = fields.Char(
        string='Individual Unique ID',
        help='MOSIP generated unique ID for individual'
    )
    aadhaar = fields.Char(
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
    government_employee_id = fields.Char(
        string='Government Employee ID',
        help='Employee ID of the government employee'
    )
    government_department = fields.Char(
        string='Government Department',
        help='Name of the government department where employed'
    )
    employee_since_date = fields.Date(
        string='Employee Since Date',
        help='Date since the individual has been employed as a government employee'
    )
    type_of_department = fields.Char(
        string='Type of Department',
        help='Type or classification of the government department'
    )
