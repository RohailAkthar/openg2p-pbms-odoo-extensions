/** @odoo-module **/

import { registry } from "@web/core/registry";

/**
 * Global removal of 'Import records' from the Odoo 17 Cog (Gear) Menu.
 * This script removes the 'import-menu' registry item so it is never
 * added to the CogMenu component, effectively hiding it from all views.
 */
registry.category("cogMenu").remove("import-menu");
