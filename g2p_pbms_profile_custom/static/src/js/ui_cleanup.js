/** @odoo-module **/

import { registry } from "@web/core/registry";

const systrayCategories = registry.category("systray");
const userMenuItems = registry.category("user_menuitems");

// 1. Remove Discuss/Messaging icon from Systray
if (systrayCategories.contains("mail.messaging_menu")) {
    systrayCategories.remove("mail.messaging_menu");
}

// 2. Remove Activities (clock) icon from Systray
if (systrayCategories.contains("mail.activity_menu")) {
    systrayCategories.remove("mail.activity_menu");
}

// 3. Remove Documentation, Support, and My Odoo.com account from User Menu
if (userMenuItems.contains("documentation")) {
    userMenuItems.remove("documentation");
}
if (userMenuItems.contains("support")) {
    userMenuItems.remove("support");
}
if (userMenuItems.contains("odoo_account")) {
    userMenuItems.remove("odoo_account");
}
