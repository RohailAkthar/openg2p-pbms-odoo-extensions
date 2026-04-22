from odoo import models, fields, api
import uuid

from .registry import G2PRegistry


class G2PRegisterFamilies(models.Model):
    _name = "g2p.register.families"
    _description = "Register Families"
    _inherit = "g2p.registry"

    functional_record_id = fields.Char(string="Functional Record ID")
    family_name = fields.Char(string="Family Name")
    type_of_housing = fields.Char(string="Type of Housing")
    house_condition = fields.Char(string="House Condition")
    sanitation_condition = fields.Char(string="Sanitation Condition")
    water_access = fields.Char(string="Water Access")
    electricity_access = fields.Char(string="Electricity Access")
    ethnic_group = fields.Char(string="Ethnic Group")
    belong_to_protected_groups = fields.Boolean(string="Belong to Protected Groups")
    under_other_vulnerable_status = fields.Boolean(string="Under Other Vulnerable Status")

    # Addl fields
    no_of_children = fields.Integer(string="No of Children")
