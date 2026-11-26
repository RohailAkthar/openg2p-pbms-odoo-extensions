/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { DomainSelector } from "@web/core/domain_selector/domain_selector";
// import { Domain, InvalidDomainError } from "@web/core/domain";
// import { EvaluationError } from "@web/core/py_js/py_builtin";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";

export class G2PBeneficiariesComponent extends Component {
    static template = "g2p_beneficiaries_info_tpl";
    static components = {
        DomainSelector
    };
    static props = {
        context: { type: Object, optional: true },
        resModel: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            title: _t("Beneficiaries"),
            records: [],
            page: 1,
            pageSize: 3,
            totalCount: 0,
            totalPages: 1,
            target_registry : this.props.record.data.target_registry,
            searched: false,  // initially hidden title and pagination
            domain : "[]",
        });
        this.orm = useService("orm");
        console.log(this);
    }

    onDomainChange(newDomain) {
        this.state.domain = newDomain;
        this.render();
    }

    getEvaluatedDomain() {
        return this.state.domain;
    }

    searchRegistrants() {
        this.state.searched = true;  // show title and pagination when search is clicked
        this.state.page = 1;
        this.state.pageSize = 20;
        this._fetchRecords();
    }

    async _fetchRecords() {
        const result = await this.orm.call(
            'g2p.bgtask.summary.wizard',
            'get_beneficiaries',
            [this.props.record.resId , this.state.page, this.state.pageSize, this.getEvaluatedDomain()],
            {},
        );
        if (result.message) {
            this.state.records = result.message.beneficiaries || [];
            this.state.totalCount = result.message.total_beneficiary_count || 0;
        } else if (result.response_body && result.response_body.response_payload) {
            // v3.1.0 staff-portal API shape:
            //   response_body.response_payload.beneficiaries
            //   response_body.pagination_response.number_of_items
            // (also the shape of Odoo's fallback when the API call failed).
            const body = result.response_body;
            const payload = body.response_payload;
            const pagination = body.pagination_response || {};
            this.state.records = payload.beneficiaries || [];
            this.state.totalCount =
                pagination.number_of_items ??
                payload.total_beneficiary_count ??
                payload.beneficiary_count ??
                0;
            if (!this.state.records.length) {
                console.warn("Beneficiary search returned no rows.", result);
            }
        } else {
            console.warn("Unrecognised beneficiary search response", result);
            this.state.records = result.records || [];
            this.state.totalCount = result.total_count || 0;
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
    extractProps({ attrs }, dynamicInfo) {
        console.log(attrs, dynamicInfo)
        return {
            resModel: attrs.model,
            context: dynamicInfo.context,
        };
    },
};
registry.category("view_widgets").add("g2p_beneficiaries_widget", g2pBeneficiariesWidget);
