import base64
from odoo import api, models, tools
from odoo.modules.module import get_resource_path


class ResCompany(models.Model):
    _inherit = "res.company"

    def get_g2p_favicon(self, img_path_module="", img_path_rel=""):
        return super().get_g2p_favicon(
            img_path_module="pbms_theme_nigeria",
            img_path_rel="static/src/img/favicon.png",
        )

    @api.model
    def _pbms_apply_branding(self):
        """Set the company favicon (the browser tab icon of the backend, served from
        /web/image/res.company/<id>/favicon by muk_web_theme) to the NSIPA logo.

        The icon lives in the database, so changing the image file alone does not change the tab.
        Runs from a <function> tag on every install/upgrade and is safe to repeat.
        """
        if "favicon" not in self._fields:
            return
        favicon = self.get_g2p_favicon()
        self.sudo().search([]).write({"favicon": favicon})

    @api.model
    def _pbms_disable_odoo_oauth(self):
        """Hide "Log in with Odoo.com" on the sign-in page.

        auth_oauth ships the "Odoo.com Accounts" provider enabled (noupdate), so it shows up on any
        server that has auth_oauth installed. Only that provider is switched off; other providers
        (for example OIDC single sign-on) are left alone. Does nothing without auth_oauth.
        """
        provider = self.env.ref("auth_oauth.provider_openerp", raise_if_not_found=False)
        if provider and provider.enabled:
            provider.sudo().write({"enabled": False})
