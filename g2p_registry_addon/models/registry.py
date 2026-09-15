from odoo import models, fields, api


class G2PRegistry(models.AbstractModel):
    _name = "g2p.registry"
    _description = "Abstract G2P Registry"

    internal_record_id = fields.Char(string="Internal Record ID")

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields=allfields, attributes=attributes)
        # Exclude internal technical fields so only base registry business columns appear in domain selector
        technical_fields = {
            "create_uid",
            "create_date",
            "write_uid",
            "write_date",
            "display_name",
            "__last_update",
            "id",
        }
        for field_name in technical_fields:
            res.pop(field_name, None)
        return res

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
