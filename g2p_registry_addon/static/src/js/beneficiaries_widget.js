/** @odoo-module **/

import { Component, useState, onWillStart, useEffect } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

export class G2PBeneficiariesComponent extends Component {
    static template = "g2p_beneficiaries_info_tpl";
    static components = {};
    static props = {
        context: { type: Object, optional: true },
        resModel: { type: String, optional: true },
        record: { type: Object, optional: true },
        readonly: { type: Boolean, optional: true },
    };

    setup() {
        const recordData = this.props.record?.data || {};
        console.log("G2PBeneficiariesComponent SETUP recordData:", recordData);
        console.log("G2PBeneficiariesComponent SETUP target_registry:", recordData.target_registry);

        this.state = useState({
            title: _t("Beneficiaries"),
            records: [],
            page: 1,
            pageSize: 50,
            totalCount: 0,
            totalPages: 1,
            target_registry: recordData.target_registry || null,
            searched: true,
            domain: "[]",
            expandedRecordId: null,
        });
        this.orm = useService("orm");

        useEffect(() => {
            if (this.props.record?.data?.target_registry) {
                this.state.target_registry = this.props.record.data.target_registry;
            }
        }, () => [this.props.record?.data?.target_registry]);

        useEffect(() => {
            console.log("G2PBeneficiariesComponent props.record:", this.props.record);
            if (this.props.record?.resId) {
                console.log("Fetching beneficiaries for resId:", this.props.record.resId);
                this._fetchRecords();
            } else {
                console.log("Skipping fetch: No resId");
            }
        }, () => [this.props.record?.resId]);
    }

    toggleDetails(recordId) {
        if (this.state.expandedRecordId === recordId) {
            this.state.expandedRecordId = null;
        } else {
            this.state.expandedRecordId = recordId;
        }
    }

    async _fetchRecords() {
        const result = await this.orm.call(
            'g2p.bgtask.summary.wizard',
            'get_beneficiaries',
            [
                [],
                this.props.record.resId,
                this.state.page,
                this.state.pageSize,
                "[('active', '=', True)]"
            ],
            {},
        );
        if (result.message) {
            this.state.records = result.message.beneficiaries;
            this.state.totalCount = result.message.total_beneficiary_count;
        } else {
            this.state.records = result.records;
            this.state.totalCount = result.total_count;
        }
        this.state.totalPages = Math.ceil(this.state.totalCount / this.state.pageSize) || 1;
    }

    async nextPage() {
        if (this.state.page < this.state.totalPages) {
            this.state.page++;
            await this._fetchRecords();
        }
    }

    async prevPage() {
        if (this.state.page > 1) {
            this.state.page--;
            await this._fetchRecords();
        }
    }
}

export const g2pBeneficiariesWidget = {
    component: G2PBeneficiariesComponent,
    extractProps({ attrs, record }, dynamicInfo) {
        return {
            resModel: attrs.model,
            context: dynamicInfo.context,
            record,
        };
    },
};
registry.category("view_widgets").add("g2p_beneficiaries_widget", g2pBeneficiariesWidget);
