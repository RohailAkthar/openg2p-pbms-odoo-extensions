from odoo import models, fields


class G2PWorkerMonthlyRegistry(models.Model):
    _name = "g2p.worker.monthly.registry"
    _description = "Worker Monthly Registry"
    _inherit = "g2p.registry"

    name = fields.Char(string="Name")
    attendance_month = fields.Char(string="Attendance Month")
    source_type = fields.Char(string="Source Type")
