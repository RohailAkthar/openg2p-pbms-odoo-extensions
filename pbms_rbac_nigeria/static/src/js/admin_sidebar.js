/** @odoo-module **/
import {NavBar} from "@web/webclient/navbar/navbar";
import {patch} from "@web/core/utils/patch";
import {onWillStart} from "@odoo/owl";
import {nsipaMenusByXmlid} from "@pbms_theme_nigeria/js/navbar_sidebar";

// The ADMINISTRATION sidebar section is only for PBMS super administrators
// (OpenG2P PBMS > Program Super Administration on the user's Access Rights).
const NSIPA_SUPER_ADMIN_GROUP = "g2p_pbms.group_program_super_administration";

// ADMINISTRATION links, resolved by menu xmlid so the ids work on any database.
const NSIPA_ADMIN_LINKS = [
    ["users", "User Access Settings", "base.menu_action_res_users"],
    ["apps", "Developer Apps", "base.menu_management"],
    ["settings", "General Settings", "base_setup.menu_config"],
];

patch(NavBar.prototype, {
    setup() {
        super.setup(...arguments);
        this.nsipaIsSuperAdmin = false;
        onWillStart(async () => {
            this.nsipaIsSuperAdmin = await this.env.services.user.hasGroup(NSIPA_SUPER_ADMIN_GROUP);
        });
    },

    // A link is also omitted when the user cannot see its menu.
    get nsipaAdminLinks() {
        if (!this.nsipaIsSuperAdmin) {
            return [];
        }
        const byXmlid = nsipaMenusByXmlid(this.menuService);
        const workspace = this._nsipaWorkspaceApp();
        const currentActionId = this._nsipaCurrentActionId();
        const links = [];
        for (const [key, label, xmlid] of NSIPA_ADMIN_LINKS) {
            const menu = byXmlid[xmlid];
            if (!menu || !menu.actionID) {
                continue;
            }
            // Keep the PBMS menu in the URL so a reload or new tab keeps the same sidebar.
            const menuId = workspace ? workspace.id : menu.id;
            links.push({
                key,
                label,
                menu,
                href: `/web#action=${menu.actionID}&menu_id=${menuId}`,
                active: !this._nsipaClickedId && menu.actionID === currentActionId,
            });
        }
        return links;
    },

    // An ADMINISTRATION page is open: no WORKSPACE entry is highlighted, and the page is
    // flagged (body.nsipa_admin_page) so its title eyebrow reads ADMINISTRATION.
    _nsipaOtherSectionActive() {
        const onAdminPage = this.nsipaAdminLinks.some((link) => link.active);
        document.body.classList.toggle("nsipa_admin_page", onAdminPage);
        return onAdminPage || super._nsipaOtherSectionActive(...arguments);
    },

    async _nsipaOpenAdminLink(ev, link) {
        if (ev.ctrlKey || ev.metaKey || ev.shiftKey || ev.button === 1) {
            return; // let the browser open the href in a new tab
        }
        ev.preventDefault();
        if (!this._nsipaWorkspaceApp()) {
            // No PBMS access: fall back to opening the menu's own app.
            return this.menuService.selectMenu(link.menu);
        }
        // Open the page without switching app, so WORKSPACE stays on PBMS.
        this._nsipaClickedId = null;
        await this.actionService.doAction(link.menu.actionID, {clearBreadcrumbs: true});
    },
});
