/** @odoo-module **/
import {ListController} from "@web/views/list/list_controller";
import {patch} from "@web/core/utils/patch";

// Presentation only: Refresh reloads the current list with the same domain/filters.
patch(ListController.prototype, {
    // "New program" opens the popup form; reloads the list once it is closed (saved or cancelled).
    onNsipaNewProgram() {
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

    // Row click on the Transfer Types list opens the read-only popup instead of the full-page form.
    async openRecord(record) {
        if (this.props.resModel === "g2p.benefit.codes") {
            const action = await this.orm.call("g2p.benefit.codes", "action_nsipa_view", [[record.resId]]);
            return this.action.doAction(action);
        }
        return super.openRecord(record);
    },

    async onNsipaRefresh() {
        await this.model.load();
        this.model.notify();
    },
});
