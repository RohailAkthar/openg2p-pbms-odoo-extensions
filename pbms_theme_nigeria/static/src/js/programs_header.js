/** @odoo-module **/
import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";

// Presentation only: Refresh reloads the current list with the same domain/filters.
patch(ListController.prototype, {
    // "New programme" opens the popup form; reloads the list once it is closed (saved or cancelled).
    onNsipaNewProgramme() {
        return this.action.doAction("pbms_theme_nigeria.action_g2p_programs_new_popup", {
            onClose: () => this.onNsipaRefresh(),
        });
    },

    // "Create code" opens the popup form; reloads the list once it is closed (saved or cancelled).
    onNsipaNewBenefitCode() {
        return this.action.doAction("pbms_theme_nigeria.action_g2p_benefit_codes_new_popup", {
            onClose: () => this.onNsipaRefresh(),
        });
    },

    // "Create sponsor bank" opens the popup form; reloads the list once it is closed.
    onNsipaNewSponsorBank() {
        return this.action.doAction("pbms_theme_nigeria.action_g2p_sponsor_bank_new_popup", {
            onClose: () => this.onNsipaRefresh(),
        });
    },

    async onNsipaRefresh() {
        await this.model.load();
        this.model.notify();
    },
});
