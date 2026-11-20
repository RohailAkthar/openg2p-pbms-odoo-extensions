/** @odoo-module **/
import {SearchBar} from "@web/search/search_bar/search_bar";
import {patch} from "@web/core/utils/patch";
import {onMounted, onPatched} from "@odoo/owl";

// Same action as pressing Enter in the search box.
patch(SearchBar.prototype, {
    setup() {
        super.setup(...arguments);
        // Approval queue only: placeholder wording from the design.
        const setPlaceholder = () => {
            const root = this.root && this.root.el;
            if (root && root.closest(".g2p-approvals-action, .nsipa_programs_list")) {
                const input = root.querySelector(".o_searchview_input");
                if (input && input.placeholder !== "Search records…") {
                    input.placeholder = "Search records…";
                }
            }
        };
        onMounted(setPlaceholder);
        onPatched(setPlaceholder);
    },

    onNsipaSearchClick() {
        if (this.state.query.length && this.items.length) {
            this.selectItem(this.items[0]);
        } else {
            this.env.searchModel.search();
        }
    },
});
