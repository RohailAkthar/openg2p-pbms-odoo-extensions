from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        """The new-user form offers an optional initial password. Left empty, the web client sends
        False, which Odoo's password inverse would try to hash ("secret must be unicode or bytes,
        not bool"); drop it so the user is created without a password (invitation flow)."""
        for vals in vals_list:
            if "password" in vals and not vals["password"]:
                del vals["password"]
        return super().create(vals_list)
