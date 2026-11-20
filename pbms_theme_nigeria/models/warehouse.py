from odoo import models


class G2PWarehouse(models.Model):
    _inherit = "g2p.warehouse"

    def action_open_edit(self):
        """Presentation only: the themed Sponsor Banks list asks for the popup form (context
        nsipa_popup); warehouses and every other caller keep the original full-page behaviour."""
        if not self.env.context.get("nsipa_popup") or not self.is_sponsor_bank:
            return super().action_open_edit()
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Edit Sponsor Bank",
            "res_model": "g2p.warehouse",
            "res_id": self.id,
            "view_mode": "form",
            "views": [[self.env.ref("pbms_theme_nigeria.view_g2p_sponsor_bank_new_popup_form").id, "form"]],
            "target": "new",
            "context": {"create": False, "warehouse_form_edit": True},
        }
