import logging

from lxml import etree
from lxml.builder import E

from odoo import api, models
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.addons.base.models.res_users import name_boolean_group, name_selection_groups

_logger = logging.getLogger(__name__)

# Role sections kept on a user's Access Rights tab (shown with and without debug mode).
# Every other section Odoo generates (User Type, Website, Administration, Job Queue, Technical,
# Extra Rights, Other) is hidden.
RBAC_ROLE_CATEGORIES = [
    "g2p_pbms.g2p_pbms",
    "g2p_documents.g2p_documents_module",
]
ADMINISTRATION_CATEGORY = "base.module_category_administration_administration"


class ResGroups(models.Model):
    _inherit = "res.groups"

    @api.model
    def _update_user_groups_view(self):
        """Odoo regenerates its Access Rights fields whenever groups change; regenerate ours after it,
        as both views depend on the database-specific field names (in_group_<id>, sel_groups_<ids>)."""
        res = super()._update_user_groups_view()
        if not self._context.get("install_filename") and not self._context.get(MODULE_UNINSTALL_FLAG):
            self._pbms_rbac_update_views()
        return res

    @api.model
    def _pbms_rbac_update_views(self):
        roles_view = self.env.ref("pbms_rbac_nigeria.view_users_form_rbac_roles", raise_if_not_found=False)
        base_view = self.env.ref("base.user_groups_view", raise_if_not_found=False)
        if not (roles_view and base_view):
            return

        admin_field = None
        sections = []
        for app, kind, groups, _category_name in self.sudo().get_groups_by_application():
            xml_id = app.get_external_id().get(app.id) if app else None
            if xml_id == ADMINISTRATION_CATEGORY and kind == "selection":
                admin_field = name_selection_groups(groups.ids)
            elif xml_id in RBAC_ROLE_CATEGORIES and kind == "boolean":
                sections.append((RBAC_ROLE_CATEGORIES.index(xml_id), app.name, groups))
        sections.sort(key=lambda s: s[0])

        self._pbms_rbac_write(roles_view, self._pbms_rbac_roles_arch(base_view, admin_field, sections))

    @api.model
    def _pbms_rbac_roles_arch(self, base_view, admin_field, sections):
        """Inherited view on top of Odoo's generated groups view: hide its sections, add ours
        (Administration dropdown, then the PBMS and Documents role checkboxes)."""
        base_arch = etree.fromstring(base_view.arch)
        nodes = []

        # Hide what Odoo generates (only nodes that exist, so the view never fails to apply).
        targets = [
            "//group[field[@widget='radio']]",  # User Type (radio buttons)
            "//group[group/field[starts-with(@name, 'sel_groups_')]]",
            "//group[@class='o_label_nowrap']",
        ]
        anchor = None
        for expr in targets:
            if base_arch.xpath(expr):
                nodes.append(
                    E.xpath(E.attribute("1", name="invisible"), expr=expr, position="attributes")
                )
                anchor = expr

        # Administration: Odoo's own dropdown (none / Access Rights / Settings), shown first.
        children = []
        if admin_field:
            children.append(E.separator(string="Administration"))
            children.append(E.group(E.field(name=admin_field, string="Administration")))
            children.append(E.group())
        # Our role sections: two columns of checkboxes per category, always visible.
        for _seq, name, groups in sections:
            children.append(E.separator(string=name))
            left, right = [], []
            for index, group in enumerate(groups):
                field = E.field(name=name_boolean_group(group.id))
                (left if index % 2 == 0 else right).append(field)
            children.append(E.group(*left))
            children.append(E.group(*right))
        roles = E.group(*children, name="pbms_rbac_roles", **{"class": "o_label_nowrap nsipa_rbac_roles"})

        if anchor:
            nodes.append(E.xpath(roles, expr=anchor, position="after"))
        else:
            nodes.append(E.xpath(roles, expr="//page[@name='access_rights']", position="inside"))
        return etree.tostring(E.data(*nodes), pretty_print=True, encoding="unicode")

    @api.model
    def _pbms_rbac_write(self, view, arch):
        if arch != view.arch:
            view.with_context(lang=None).sudo().write({"arch": arch})
