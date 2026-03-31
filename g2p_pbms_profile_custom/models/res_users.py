# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from lxml import etree

class ResGroups(models.Model):
    _inherit = 'res.groups'

    @api.model
    def _update_user_groups_view(self):
        """
        Override to make OpenG2P PBMS and OpenG2P Documents sections visible 
        in normal mode (not just debug mode).
        """
        super(ResGroups, self)._update_user_groups_view()
        view = self.env.ref('base.user_groups_view', raise_if_not_found=False)
        if not view or not view.arch:
            return

        arch = etree.fromstring(view.arch)
        # Find the group that has groups="base.group_no_one" and contains separators
        # This is typically the last group in the 'groups_id' field.
        # In Odoo 17, it's inside <field name="groups_id" position="replace">
        restricted_group = arch.xpath("//group[@groups='base.group_no_one' and separator]")
        if not restricted_group:
            return
        
        restricted_group = restricted_group[-1] # Usually the one with xml4 contents
        
        # We want to identify the OpenG2P separators and the groups that follow them
        # until the next separator.
        openg2p_strings = ['OpenG2P PBMS', 'OpenG2P Documents Module']
        
        new_visible_group = etree.Element('group')
        # Copy attributes except 'groups' if any
        for key, value in restricted_group.attrib.items():
            if key != 'groups':
                new_visible_group.set(key, value)
        
        nodes_to_move = []
        moving = False
        for child in list(restricted_group):
            if child.tag == 'separator' and child.get('string') in openg2p_strings:
                moving = True
            elif child.tag == 'separator' and moving:
                moving = False
            
            if moving:
                nodes_to_move.append(child)
        
        if nodes_to_move:
            for node in nodes_to_move:
                restricted_group.remove(node)
                new_visible_group.append(node)
            
            # Insert the new visible group before the restricted group
            restricted_group.addprevious(new_visible_group)
        
        # Remove Website section (can be a separator or a group)
        strings_to_remove = ['Website', 'WEBSITE', 'Website Section']
        for node in arch.xpath("//separator | //group"):
            if node.get('string') in strings_to_remove:
                # If it's a separator in the restricted group, we might need 
                # to remove the following fields too. 
                # But if it's in a selection group (xml3), removing the group is enough.
                parent = node.getparent()
                if parent is not None:
                    if node.tag == 'separator':
                        # Look for following group/field nodes until next separator
                        to_remove = [node]
                        for sibling in node.itersiblings():
                            if sibling.tag == 'separator':
                                break
                            to_remove.append(sibling)
                        for n in to_remove:
                            parent.remove(n)
                    else:
                        # It's a group, just remove it
                        parent.remove(node)
            
        # Serialize and update
        new_arch = etree.tostring(arch, encoding='unicode', pretty_print=True)
        view.sudo().write({'arch': new_arch})


class ChangePasswordWizard(models.TransientModel):
    _inherit = "change.password.wizard"

    user_id_display = fields.Many2one('res.users', string='User', readonly=True)
    user_login_display = fields.Char(string='User Login', readonly=True)
    new_passwd_display = fields.Char(string='New Password')

    @api.model
    def default_get(self, fields):
        res = super(ChangePasswordWizard, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        if active_ids and len(active_ids) == 1:
            user = self.env['res.users'].browse(active_ids[0])
            res.update({
                'user_id_display': user.id,
                'user_login_display': user.login,
            })
        return res

    def change_password_button(self):
        self.ensure_one()
        if self.user_id_display and self.new_passwd_display:
            # Single-user mode
            self.user_id_display._change_password(self.new_passwd_display)
            if self.env.user == self.user_id_display:
                return {'type': 'ir.actions.client', 'tag': 'reload'}
            return {'type': 'ir.actions.act_window_close'}
        return super(ChangePasswordWizard, self).change_password_button()
