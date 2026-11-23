/** @odoo-module **/
import {NavBar} from "@web/webclient/navbar/navbar";
import {patch} from "@web/core/utils/patch";
import {useBus} from "@web/core/utils/hooks";
import {onMounted, onPatched} from "@odoo/owl";

// The WORKSPACE sidebar always shows the PBMS app's menus, whatever page is open.
const NSIPA_WORKSPACE_APP = "g2p_pbms.menu_g2p_root";

export function nsipaMenusByXmlid(menuService) {
    const byXmlid = {};
    for (const menu of menuService.getAll()) {
        if (menu.xmlid) {
            byXmlid[menu.xmlid] = menu;
        }
    }
    return byXmlid;
}

// Layout/presentation only: marks the current top-level section in the sidebar
// (CSS class `nsipa_active`) and keeps all entries visible on desktop.
patch(NavBar.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => this._nsipaMarkActive());
        onPatched(() => this._nsipaMarkActive());
        // Re-render when the page changes so the active entry follows it.
        useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", () => this.render());
    },

    // Pin the sidebar to PBMS. Users without access to PBMS keep Odoo's behaviour.
    get currentApp() {
        return this._nsipaWorkspaceApp() || super.currentApp;
    },

    _nsipaWorkspaceApp() {
        return nsipaMenusByXmlid(this.menuService)[NSIPA_WORKSPACE_APP];
    },

    _nsipaCurrentActionId() {
        const controller = this.actionService.currentController;
        return controller && controller.action && controller.action.id;
    },

    // Hook for other sidebar sections (e.g. ADMINISTRATION in pbms_rbac_nigeria): return true
    // while one of their pages is open, so no WORKSPACE entry is highlighted at the same time.
    _nsipaOtherSectionActive() {
        return false;
    },

    _nsipaMarkActive() {
        const root = this.root && this.root.el;
        if (!root) {
            return;
        }
        for (const el of root.querySelectorAll(".o_menu_sections .nsipa_active")) {
            el.classList.remove("nsipa_active");
        }
        if (this._nsipaOtherSectionActive()) {
            return;
        }
        const app = this.currentApp;
        // The clicked menu is known immediately; the URL hash can lag one render behind.
        const menuId =
            this._nsipaClickedId || parseInt(this.env.services.router.current.hash.menu_id, 10);
        let activeId = null;
        if (app) {
            for (const section of this.menuService.getMenuAsTree(app.id).childrenTree || []) {
                const stack = [section];
                while (stack.length) {
                    const node = stack.pop();
                    if (node.id === menuId) {
                        activeId = section.id;
                    }
                    stack.push(...(node.childrenTree || []));
                }
            }
        }
        if (activeId !== null) {
            const target = root.querySelector(`.o_menu_sections [data-section="${activeId}"]`);
            const entry = target && target.closest(".o_nav_entry, .dropdown-toggle");
            if (entry) {
                entry.classList.add("nsipa_active");
            }
        }
    },

    onNavBarDropdownItemSelection(menu) {
        if (menu && menu.id) {
            this._nsipaClickedId = menu.id;
            this._nsipaMarkActive();
        }
        return super.onNavBarDropdownItemSelection(...arguments);
    },

    async adapt() {
        if (window.matchMedia("(min-width: 768px)").matches) {
            return;
        }
        return super.adapt(...arguments);
    },
});
