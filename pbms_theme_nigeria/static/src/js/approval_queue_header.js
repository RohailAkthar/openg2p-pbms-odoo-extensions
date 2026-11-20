/** @odoo-module **/
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";

// Presentation only: the header's Refresh button re-creates the current list view
// so it reloads its data. No change to domains, columns or approval logic.
const ApprovalsAction = registry.category("actions").get("g2p_approvals_tabbed", null);
if (ApprovalsAction) {
    patch(ApprovalsAction.prototype, {
        setup() {
            super.setup(...arguments);
            this.state.nsipaRefresh = 0;
        },
        // 10 records per page on both tabs (Odoo's default is 80).
        get queueViewProps() {
            return {...super.queueViewProps, limit: 10};
        },
        get historyViewProps() {
            return {...super.historyViewProps, limit: 10};
        },
        onNsipaRefresh() {
            this.state.nsipaRefresh = (this.state.nsipaRefresh || 0) + 1;
        },
    });
}
