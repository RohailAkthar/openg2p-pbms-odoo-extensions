import base64
from odoo import tools
from odoo.modules.module import get_resource_path
from . import models


def post_init_hook(env):
    try:
        logo_path = get_resource_path(
            "pbms_theme_nigeria", "static/src/img/nigeria_coat_of_arms.png"
        )
        if logo_path:
            with tools.file_open(logo_path, "rb") as f:
                logo_data = base64.b64encode(f.read())
            companies = env["res.company"].sudo().search([])
            for comp in companies:
                comp.sudo().write({"logo": logo_data})
    except Exception:
        pass
