/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { G2PBeneficiariesComponent } from "@g2p_registry_addon/js/beneficiaries_widget";

patch(G2PBeneficiariesComponent.prototype, {
    setup() {
        super.setup();
        const recordData = this.props.record?.data || {};
        this.state.list_stage = recordData.list_stage || null;
        this.state.isDisbursement = (this.state.list_stage === 'disbursement');
    },

    downloadBeneficiariesCSV() {
        const wizardId = this.props.record?.resId;
        if (!wizardId) {
            return;
        }
        const domain = encodeURIComponent(this.getEvaluatedDomain() || "[]");
        window.location.href = `/g2p/export_disbursement_beneficiaries?wizard_id=${wizardId}&domain=${domain}`;
    }
});
