# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class PBMSDashboardController(http.Controller):
    def _access_denied_response(self):
        response = request.render('g2p_pbms_dashboard.dashboard_access_denied')
        response.status_code = 403
        return response

    def _ensure_dashboard_user(self, redirect_target):
        if not request.session.uid:
            return request.redirect(f"/web/login?redirect={redirect_target}")
        if not request.env.user.has_group('g2p_pbms_dashboard.group_dashboard_viewer'):
            request.session.logout(keep_db=True)
            return self._access_denied_response()
        return None

    @http.route('/dashboard', type='http', auth='public', website=True)
    def dashboard(self, **kwargs):
        """Route for dedicated dashboard access"""
        blocked = self._ensure_dashboard_user('/dashboard')
        if blocked:
            return blocked
        
        # Render simple template that will load the dashboard
        return request.render('g2p_pbms_dashboard.dashboard_template', {
            'dashboard_type': 'beneficiary',
        })

    @http.route('/dashboard/minimal', type='http', auth='public', website=True)
    def dashboard_minimal(self, **kwargs):
        """Alternative route that opens the dashboard in minimal web client."""
        blocked = self._ensure_dashboard_user('/dashboard/minimal')
        if blocked:
            return blocked

        return request.redirect('/web?minimal=1#action=g2p_pbms_dashboard.pbms_dashboard_action')
