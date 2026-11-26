from odoo import models


class G2PBenefitCodes(models.Model):
    _inherit = "g2p.benefit.codes"

    def action_open_edit(self):
        """Presentation only: the themed Transfer Types list asks for the popup form
        (context nsipa_popup); every other caller keeps the original full-page behaviour."""
        if not self.env.context.get("nsipa_popup"):
            return super().action_open_edit()
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Edit Transfer Type",
            "res_model": "g2p.benefit.codes",
            "res_id": self.id,
            "view_mode": "form",
            "views": [[self.env.ref("pbms_theme_nigeria.view_g2p_benefit_codes_new_popup_form").id, "form"]],
            "target": "new",
            "context": {"create": False, "benefit_code_form_edit": True},
        }

    def action_nsipa_view(self):
        """Presentation only: row click in the themed Transfer Types list opens the same popup form,
        read-only (benefit_code_form_edit is not set, so every field is read-only and Save is hidden)."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Transfer Type",
            "res_model": "g2p.benefit.codes",
            "res_id": self.id,
            "view_mode": "form",
            "views": [[self.env.ref("pbms_theme_nigeria.view_g2p_benefit_codes_new_popup_form").id, "form"]],
            "target": "new",
            "context": {"create": False, "edit": False, "benefit_code_form_edit": False},
        }
