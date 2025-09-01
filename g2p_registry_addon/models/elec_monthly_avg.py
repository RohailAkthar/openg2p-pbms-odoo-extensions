from odoo import models, fields, api


class G2PRegistryElecMonthlyAvg(models.Model):
    """Electricity Six-Monthly Average Consumption Registry Model"""
    _name = 'g2p.registry.elec.monthly.avg'
    _description = 'Electricity Monthly Average Consumption Registry'
    _inherit = 'g2p.registry'

    id = fields.Integer(
        string='ID',
        help='Primary key identifier for the electricity monthly average record'
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
    date_of_computation = fields.Date(
        string='Date of Computation',
        help='Date when the six-month average was computed'
    )
    six_month_avg_units = fields.Float(
        string='Six Month Average Units',
        help='Average electricity units consumed over six months'
    )
    six_month_avg_amount = fields.Float(
        string='Six Month Average Amount',
        help='Average electricity amount billed over six months'
    )