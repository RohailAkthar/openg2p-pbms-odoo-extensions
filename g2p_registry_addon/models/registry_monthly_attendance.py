from odoo import models, fields


class G2PRegistryMonthlyAttendance(models.Model):
    _name = "g2p.registry.monthly.attendance"
    _description = "Monthly Attendance Registry"
    _inherit = "g2p.registry"

    nrc_number = fields.Char(string="NRC Number")
    attendance_month = fields.Date(string="Attendance Month")
    number_of_days = fields.Integer(string="Number of Days")
