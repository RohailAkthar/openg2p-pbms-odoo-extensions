from odoo import http
from odoo.http import request
from odoo.tools.translate import _

from odoo.addons.web.controllers.home import Home


class WebLoginHome(Home):
    @http.route()
    def web_login(self, redirect=None, **kw):
        response = super().web_login(redirect=redirect, **kw)
        if hasattr(response, "qcontext"):
            response.qcontext["title"] = "Login | Gramstack"
            if "error" in response.qcontext:
                error_message = response.qcontext["error"]
                if error_message == _("Wrong login/password"):
                    response.qcontext["error"] = _("Login failed due to Invalid credentials !")
        return response

    @http.route(["/favicon.ico"], type="http", auth="public", website=True, multilang=False, sitemap=False)
    def favicon(self, **kw):
        return request.redirect("/pbms_theme_extension/static/src/img/favicon-gramstack.png?v=2", code=301)
