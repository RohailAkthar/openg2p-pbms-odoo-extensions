from odoo import models, fields


class G2PRegistryMonthlyAvailability(models.Model):
    _name = "g2p.registry.monthly.availability"
    _description = "Monthly Availability Registry"
    _inherit = "g2p.registry"

    name = fields.Char(string="Name")
    attendance_month_str = fields.Char(string="Attendance Month (String)")
    attendance_month = fields.Date(string="Attendance Month")
    source_type = fields.Char(string="Source Type")
