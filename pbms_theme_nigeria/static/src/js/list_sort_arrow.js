/** @odoo-module **/
import {ListRenderer} from "@web/views/list/list_renderer";
import {patch} from "@web/core/utils/patch";

// Presentation only: the sort arrow in the "New programme" popup tables stays hidden until the
// user clicks a column header. Sorting itself (default order and click-to-sort) is unchanged.
patch(ListRenderer.prototype, {
    onClickSortColumn(column) {
        const root = this.rootRef && this.rootRef.el;
        if (root) {
            root.dataset.nsipaSorted = "1";
        }
        return super.onClickSortColumn(...arguments);
    },
});
