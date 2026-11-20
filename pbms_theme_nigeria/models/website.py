import base64

from odoo import api, models, tools


class Website(models.Model):
    _inherit = "website"

    @api.model
    def _pbms_apply_branding(self):
        """Name the website and set its favicon, so the sign-in tab reads "Login | PBMS" with the NSIPA icon.

        The stock website records are noupdate, so plain XML data would be skipped on upgrade; this runs
        from a <function> tag instead and is safe to run repeatedly.
        """
        with tools.file_open("pbms_theme_nigeria/static/src/img/nsipa_favicon.png", "rb") as f:
            favicon = base64.b64encode(f.read())
        self.sudo().search([]).write({"name": "PBMS", "favicon": favicon})
