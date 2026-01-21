/** @odoo-module **/

import { Component, useState, useEffect } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

export class G2PBeneficiariesComponent extends Component {
    static template = "g2p_beneficiaries_info_tpl";
    static props = {
        context: { type: Object, optional: true },
        resModel: { type: String, optional: true },
        record: { type: Object, optional: true },
        readonly: { type: Boolean, optional: true },
    };
    _t = _t;

    setup() {
        // Fallback: Try to get record from the environment model if props are missing
        // This is crucial for Form View widgets where props might not be injected correctly
        let record = this.props.record;
        if ((!record || !record.resId) && this.env.model && this.env.model.root) {
            record = this.env.model.root;
            console.log("G2PBeneficiariesComponent: Using fallback record from env.model.root", record);
        }

        const recordData = record?.data || {};

        this.state = useState({
            title: _t("Beneficiaries"),
            records: [],
            page: 1,
            pageSize: 50,
            totalCount: 0,
            totalPages: 1,
            target_registry: recordData.target_registry || null,
            expandedRecordId: null,
            loading: false,
        });

        this.orm = useService("orm");

        // Sync target_registry if it changes (e.g. record update in parent view)
        useEffect(() => {
            // Re-evaluate record source inside effect to ensure freshness
            let currentRecord = this.props.record;
            if ((!currentRecord || !currentRecord.resId) && this.env.model && this.env.model.root) {
                currentRecord = this.env.model.root;
            }

            if (currentRecord?.data?.target_registry) {
                this.state.target_registry = currentRecord.data.target_registry;
            }
        }, () => [this.props.record?.data?.target_registry, this.env.model?.root?.data?.target_registry]);

        // Fetch beneficiaries whenever resId changes
        useEffect(() => {
            let currentRecord = this.props.record;
            if ((!currentRecord || !currentRecord.resId) && this.env.model && this.env.model.root) {
                currentRecord = this.env.model.root;
            }

            const resId = currentRecord?.resId || currentRecord?.data?.id;

            if (resId) {
                console.log("Fetching beneficiaries for resId:", resId);
                this._fetchRecords(resId);
            } else {
                console.log("G2PBeneficiariesComponent: No record selected.");
            }
        }, () => [this.props.record?.resId, this.env.model?.root?.resId]);
    }

    toggleDetails(recordId) {
        if (this.state.expandedRecordId === recordId) {
            this.state.expandedRecordId = null;
        } else {
            this.state.expandedRecordId = recordId;
        }
    }

    async _fetchRecords(resId) {
        this.state.loading = true;
        try {
            const result = await this.orm.call(
                'g2p.bgtask.summary.wizard',
                'get_beneficiaries',
                [
                    resId,
                    this.state.page,
                    this.state.pageSize,
                    "[('active', '=', True)]" // Python string domain safe_eval
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
        } catch (e) {
            console.error("Error fetching beneficiaries:", e);
            this.state.records = [];
        } finally {
            this.state.loading = false;
        }
    }

    async nextPage() {
        if (this.state.page < this.state.totalPages) {
            this.state.page++;
            // Re-fetch using current record availability
            let currentRecord = this.props.record;
            if ((!currentRecord || !currentRecord.resId) && this.env.model && this.env.model.root) {
                currentRecord = this.env.model.root;
            }
            const resId = currentRecord?.resId || currentRecord?.data?.id;
            if (resId) {
                await this._fetchRecords(resId);
            }
        }
    }

    async prevPage() {
        if (this.state.page > 1) {
            this.state.page--;
            let currentRecord = this.props.record;
            if ((!currentRecord || !currentRecord.resId) && this.env.model && this.env.model.root) {
                currentRecord = this.env.model.root;
            }
            const resId = currentRecord?.resId || currentRecord?.data?.id;
            if (resId) {
                await this._fetchRecords(resId);
            }
        }
    }
}

export const g2pBeneficiariesWidget = {
    component: G2PBeneficiariesComponent,
    extractProps(nodeInfo, dynamicInfo) {
        // Robust extraction attempting multiple sources
        return {
            resModel: nodeInfo.attrs.model,
            context: dynamicInfo.context,
            record: dynamicInfo.record || nodeInfo.record,
        };
    },
};
registry.category("view_widgets").add("g2p_beneficiaries_widget", g2pBeneficiariesWidget);
