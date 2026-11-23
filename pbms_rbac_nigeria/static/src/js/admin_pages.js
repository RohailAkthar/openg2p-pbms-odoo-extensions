/** @odoo-module **/
import {ListController} from "@web/views/list/list_controller";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {FormController} from "@web/views/form/form_controller";
import {SettingsFormController} from "@web/webclient/settings_form_view/settings_form_controller";
import {patch} from "@web/core/utils/patch";

// ADMINISTRATION screens reuse the PBMS card layout (`nsipa_programs_list`): page header,
// "N records" + search on top, table / cards in the middle, pager as the footer.
// Presentation only; not applied inside dialogs (e.g. "select users" pop-ups).
const NSIPA_ADMIN_SCREENS = {
    list: {"res.users": "users"},
    kanban: {"ir.module.module": "apps"},
    form: {"res.users": "user"},
};

// "New user" opens this compact pop-up (Name, Email, Administration) instead of the full page.
const NSIPA_NEW_USER_POPUP = "pbms_rbac_nigeria.action_res_users_new_popup";

function nsipaAdminScreen(controller, viewType) {
    if (controller.env.inDialog) {
        return null;
    }
    return NSIPA_ADMIN_SCREENS[viewType][controller.props.resModel] || null;
}

function nsipaClassName(className, screen) {
    return screen ? `${className || ""} nsipa_programs_list nsipa_admin_view nsipa_admin_${screen}` : className;
}

function nsipaOpenNewUserPopup(actionService, onClose) {
    return actionService.doAction(NSIPA_NEW_USER_POPUP, {onClose});
}

patch(ListController.prototype, {
    get nsipaAdminScreen() {
        return nsipaAdminScreen(this, "list");
    },
    get className() {
        return nsipaClassName(super.className, this.nsipaAdminScreen);
    },
    // "+ New user": pop-up; the list reloads once it is closed (saved or discarded).
    onNsipaNewUser() {
        return nsipaOpenNewUserPopup(this.actionService, () => this.onNsipaRefresh());
    },
});

patch(KanbanController.prototype, {
    get nsipaAdminScreen() {
        return nsipaAdminScreen(this, "kanban");
    },
    get className() {
        return nsipaClassName(super.className, this.nsipaAdminScreen);
    },

    async onNsipaRefresh() {
        await this.model.load();
        this.model.notify();
    },

    // "Update apps list" opens Odoo's own wizard; the cards reload once it is closed.
    onNsipaUpdateApps() {
        return this.actionService.doAction("base.action_view_base_module_update", {
            onClose: () => this.onNsipaRefresh(),
        });
    },
});

patch(FormController.prototype, {
    get nsipaAdminScreen() {
        return nsipaAdminScreen(this, "form");
    },
    get className() {
        // Only marker classes here (no card layout): used to hide the record pager on a user page.
        const result = super.className; // an object {class: bool} for form views
        if (this.nsipaAdminScreen) {
            result[`nsipa_admin_view nsipa_admin_${this.nsipaAdminScreen}`] = true;
        } else if (this.env.inDialog && this.props.resModel === "res.users") {
            result.nsipa_user_popup = true; // "New user" pop-up styling (user_access.scss)
        }
        return result;
    },
    // "+ New" on a user page opens the same pop-up instead of an empty full-page form.
    async create() {
        if (this.nsipaAdminScreen !== "user") {
            return super.create(...arguments);
        }
        const dirty = await this.model.root.isDirty();
        const canProceed = !dirty || (await this.model.root.save({onError: this.onSaveError.bind(this)}));
        if (canProceed) {
            return nsipaOpenNewUserPopup(this.actionService, () => this.model.load());
        }
    },
});

// General Settings shows only the G2P PBMS Settings tab: Odoo's General Settings and Website
// tabs are hidden (admin_pages.scss), so the page opens on G2P PBMS Settings instead of them.
const NSIPA_SETTINGS_TAB = "g2p_config_settings";
const NSIPA_HIDDEN_SETTINGS_TABS = ["", "general_settings", "website"];

patch(SettingsFormController.prototype, {
    setup() {
        super.setup(...arguments);
        const arch = typeof this.props.arch === "string" ? this.props.arch : this.props.arch?.outerHTML || "";
        if (NSIPA_HIDDEN_SETTINGS_TABS.includes(this.initialApp) && arch.includes(`name="${NSIPA_SETTINGS_TAB}"`)) {
            this.initialApp = NSIPA_SETTINGS_TAB;
        }
    },
});
