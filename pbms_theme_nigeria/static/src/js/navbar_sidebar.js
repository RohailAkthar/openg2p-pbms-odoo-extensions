/** @odoo-module **/
import {NavBar} from "@web/webclient/navbar/navbar";
import {patch} from "@web/core/utils/patch";
import {onMounted, onPatched} from "@odoo/owl";

// Layout/presentation only: marks the current top-level section in the sidebar
// (CSS class `nsipa_active`) and keeps all entries visible on desktop.
patch(NavBar.prototype, {
    setup() {
        super.setup(...arguments);
        onMounted(() => this._nsipaMarkActive());
        onPatched(() => this._nsipaMarkActive());
    },

    _nsipaMarkActive() {
        const root = this.root && this.root.el;
        if (!root) {
            return;
        }
        const app = this.menuService.getCurrentApp();
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
        for (const el of root.querySelectorAll(".nsipa_active")) {
            el.classList.remove("nsipa_active");
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
