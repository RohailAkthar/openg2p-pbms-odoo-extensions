/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";

function cleanupRegistries() {
    const menuCategories = ["user_menuitems", "user_menu"];
    const toRemoveUserMenu = ["documentation", "support", "shortcuts", "odoo_account", "account"];

    for (const catName of menuCategories) {
        const userMenuRegistry = registry.category(catName);
        for (const key of toRemoveUserMenu) {
            if (userMenuRegistry.contains(key)) {
                userMenuRegistry.remove(key);
            }
        }
    }

    const systrayRegistry = registry.category("systray");
    const toRemoveSystray = [];
    for (const [key] of systrayRegistry.getEntries()) {
        if (
            key.includes("mail") ||
            key.includes("messaging") ||
            key.includes("activity") ||
            key.includes("chat") ||
            key.includes("Mail") ||
            key.includes("Activity")
        ) {
            toRemoveSystray.push(key);
        }
    }
    for (const key of toRemoveSystray) {
        systrayRegistry.remove(key);
    }
}

patch(WebClient.prototype, {
    setup() {
        super.setup();
        this.title.setParts({ zopenerp: "PBMS" });
        cleanupRegistries();
    },
});

cleanupRegistries();
