from odoo import models, fields


class G2PWorkerRegistry(models.Model):
    _name = "g2p.worker.registry"
    _description = "Worker Registry"
    _inherit = "g2p.registry"

    name = fields.Char(string="Name", required=True)
    email = fields.Char(string="Email", required=True)
    phone = fields.Char(string="Phone", required=True)

    province_id = fields.Integer(string="Province ID")
    district_id = fields.Integer(string="District ID")
    constituency_id = fields.Integer(string="Constituency ID")
    ward_id = fields.Integer(string="Ward ID")