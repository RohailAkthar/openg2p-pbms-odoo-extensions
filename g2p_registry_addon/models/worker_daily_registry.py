from odoo import models, fields


class G2PWorkerDailyRegistry(models.Model):
    _name = "g2p.worker.daily.registry"
    _description = "Worker Daily Registry"
    _inherit = "g2p.registry"

    nrc_number = fields.Char(string="NRC Number")
    attendance_date = fields.Date(string="Attendance Date")
    task = fields.Text(string="Task")
