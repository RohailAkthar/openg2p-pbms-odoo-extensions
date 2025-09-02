from odoo import models, fields


class G2PRegistry(models.AbstractModel):
    _name = "g2p.registry"
    _description = "Abstract G2P Registry"

    id = fields.Integer(
        string='ID',
        help='Primary key identifier for the record'
    )
    unique_id = fields.Char(string="Unique ID", required=False)

    def action_open_view(self):
        return {
            "type": "ir.actions.act_window",
            "name": "View Registry Record",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "flags": {"mode": "readonly"},
        }
