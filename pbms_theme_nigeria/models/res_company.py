import base64
from odoo import models, tools
from odoo.modules.module import get_resource_path


class ResCompany(models.Model):
    _inherit = "res.company"

    def get_g2p_favicon(self, img_path_module="", img_path_rel=""):
        return super().get_g2p_favicon(
            img_path_module="pbms_theme_nigeria",
            img_path_rel="static/src/img/favicon.png",
        )
