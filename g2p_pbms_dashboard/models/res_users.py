from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    dashboard_viewer = fields.Boolean(
        string="Dashboard Viewer",
        compute="_compute_dashboard_viewer",
        inverse="_inverse_dashboard_viewer",
        readonly=False,
    )

    @api.depends("groups_id")
    def _compute_dashboard_viewer(self):
        group = self.env.ref("g2p_pbms_dashboard.group_dashboard_viewer", raise_if_not_found=False)
        for user in self:
            user.dashboard_viewer = bool(group and group in user.groups_id)

    def _inverse_dashboard_viewer(self):
        group = self.env.ref("g2p_pbms_dashboard.group_dashboard_viewer", raise_if_not_found=False)
        if not group:
            return
        for user in self:
            if user.dashboard_viewer:
                user.groups_id = [(4, group.id)]
            else:
                user.groups_id = [(3, group.id)]
