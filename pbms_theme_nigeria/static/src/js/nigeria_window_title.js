/** @odoo-module **/
import {WebClient} from "@web/webclient/webclient";
import {patch} from "@web/core/utils/patch";

patch(WebClient.prototype, {
    setup() {
        super.setup();
<<<<<<< HEAD
        this.title.setParts({zopenerp: "Nigeria - PBMS"});
=======
        this.title.setParts({zopenerp: "NSIPA - PBMS"});
>>>>>>> 4bc2c75 (Align with the UI/UX team)
    },
});
