from odoo import models, fields, api, _
from odoo.http import request

class ResUsers(models.Model):
    _inherit = 'res.users'

    def _update_last_login(self):
        super(ResUsers, self)._update_last_login()
        for user in self:
            # Skip public user noise
            if user.id == self.env.ref('base.public_user').id:
                continue
                
            # Dynamic PBMS group detection (High Level Groups only)
            pbms_cat = self.env.ref('g2p_pbms.g2p_pbms', raise_if_not_found=False)
            if pbms_cat:
                # Find all groups in the PBMS category
                all_pbms_groups = self.env['res.groups'].sudo().search([('category_id', '=', pbms_cat.id)])
                
                # Identify "Low Level Groups" (those implied by any other group in this category)
                all_implied_ids = set()
                for g in all_pbms_groups:
                    all_implied_ids.update(g.implied_ids.ids)
                
                # High Level Groups are those NOT implied by others in this category
                groups = user.groups_id.filtered(lambda g: g.category_id == pbms_cat and g.id not in all_implied_ids)
                
                if groups:
                    user_type = ", ".join(groups.mapped('name'))
                else:
                    user_type = 'Internal User'
            else:
                user_type = 'Internal User'

            # Create session audit record
            self.env['user.session.audit'].sudo().create({
                'user_id': user.id,
                'login_date': fields.Datetime.now(),
                'ip_address': request.httprequest.remote_addr if request else False,
                'user_agent': request.httprequest.user_agent.string if request else False,
                'session_id': request.session.sid if request else False,
                'user_type': user_type,
            })
        return True
