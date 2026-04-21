/** @odoo-module */

import { Component, useState, onWillStart, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";
import { MapComponent } from "@g2p_pbms_dashboard/components/map/map_component";
import { ChartComponent } from "@g2p_pbms_dashboard/components/chart/chart";
import { KpiComponent } from "@g2p_pbms_dashboard/components/kpi/kpi";

export class PBMSDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.dashboardType = this.props.action.context.dashboard_type || 'beneficiary';
        const savedLang = window.localStorage.getItem("pbms_dashboard_lang");
        this.state = useState({
            kpi: {
                total_enrolled: 0,
                total_disbursed_amount: 0,
                total_budget_allocated: 0,
                program_count: 0
            },
            charts: {
                age: {},
                gender: {},
                region: {},
                monetary_program_data: {},
                monetary_region_data: {},
            },
            map_data: {},
            map_geojson: {
                provinces: { type: "FeatureCollection", features: [] },
                districts: { type: "FeatureCollection", features: [] }
            },
            programs: [],
            loading: true,
            filters: {
                gender: null,
                age_bucket: null,
                region: null,
                district: null,
                program_id: null,
            },
            activeTab: 'summary',
            beneficiaries: {
                data: [],
                total: 0,
                page: 1,
                pageSize: 20,
                loading: false
            },
            searchTerm: '',
            currentUserName: session.name || session.username || "Dashboard User",
            currentLang: savedLang === "sw" ? "sw" : "en_US",
        });

        // Bind methods
        this.applyFilterFromChart = this.applyFilterFromChart.bind(this);
        this.applyFilterFromMap = this.applyFilterFromMap.bind(this);
        this.clearFilters = this.clearFilters.bind(this);
        this.fetchData = this.fetchData.bind(this);
        this.logout = this.logout.bind(this);
        this.switchLanguage = this.switchLanguage.bind(this);

        // Load initial data
        onWillStart(async () => {
            await this.fetchData();
        });

        // Apply immediately to avoid navbar flicker before first paint.
        document.body.classList.add("o_pbms_dashboard_mode");

        onWillUnmount(() => {
            document.body.classList.remove("o_pbms_dashboard_mode");
        });
    }

    async fetchData() {
        try {
            this.state.loading = true;

            // Get dashboard data using ORM call to our logic model
            const data = await this.orm.call(
                "g2p.pbms.dashboard.logic",
                "get_dashboard_data",
                [],
                {
                    filters: this.state.filters,
                    dashboard_type: this.dashboardType
                }
            );

            if (data) {
                // Update KPIs
                this.state.kpi = data.kpi;

                // Update charts data
                this.state.charts = data.charts;

                // Update map data
                this.state.map_data = data.map_data;

                // Update map GeoJSON
                if (data.map_geojson) {
                    this.state.map_geojson = data.map_geojson;
                }

                // Load programs
                this.state.programs = data.programs;
            }

        } catch (error) {
            console.error('Error fetching dashboard data:', error);
        } finally {
            this.state.loading = false;
        }
    }

    setFilterProgram(programId) {
        this.state.filters.program_id = programId ? parseInt(programId) : null;
        this.fetchData();
    }

    setFilterGender(gender) {
        this.state.filters.gender = gender || null;
        this.fetchData();
    }

    setFilterAgeBucket(bucket) {
        this.state.filters.age_bucket = bucket || null;
        this.fetchData();
    }

    applyFilterFromChart(payload) {
        if (!payload || !payload.chartType) return;

        if (payload.chartType === "gender") {
            const g = payload.label === "Male" ? "male" : payload.label === "Female" ? "female" : null;
            this.state.filters.gender = this.state.filters.gender === g ? null : g;
        } else if (payload.chartType === "age") {
            const key = payload.label;
            this.state.filters.age_bucket = this.state.filters.age_bucket === key ? null : key;
        } else if (payload.chartType === "region") {
            const level = (this.state.charts?.region_data && this.state.charts.region_data.level) || "province";
            const key = payload.key || payload.label;
            if (level === "district") {
                this.state.filters.district = this.state.filters.district === key ? null : key;
            } else {
                this.state.filters.region = this.state.filters.region === key ? null : key;
                this.state.filters.district = null;
            }
        }
        this.fetchData();
    }

    applyFilterFromMap(payload) {
        if (!payload) return;

        let changed = false;
        if (payload.region !== undefined && this.state.filters.region !== payload.region) {
            this.state.filters.region = payload.region;
            this.state.filters.district = null;
            changed = true;
        }
        if (payload.district !== undefined && this.state.filters.district !== payload.district) {
            this.state.filters.district = this.state.filters.district === payload.district ? null : payload.district;
            changed = true;
        }

        if (changed) {
            this.fetchData();
        }
    }

    clearFilters() {
        this.state.filters = {
            gender: null,
            age_bucket: null,
            region: null,
            district: null,
            program_id: null
        };
        this.fetchData();
    }

    get hasActiveFilters() {
        return Object.values(this.state.filters).some(v => v !== null);
    }

    switchDashboardType(type) {
        this.dashboardType = type;
        this.state.filters = {
            gender: null,
            age_bucket: null,
            region: null,
            district: null,
            program_id: null
        };
        this.fetchData();
    }

    logout() {
        window.location.href = "/web/session/logout?redirect=/web";
    }

    switchLanguage(langCode) {
        if (!langCode || this.state.currentLang === langCode) {
            return;
        }
        this.state.currentLang = langCode;
        window.localStorage.setItem("pbms_dashboard_lang", langCode);
    }

    get isSwahili() {
        return this.state.currentLang === "sw";
    }

    translate(text) {
        const sw = {
            "PBMS Dashboard": "Dashibodi ya PBMS",
            "Refine Data": "Chuja Data",
            "Program": "Mpango",
            "All Programs": "Mipango Yote",
            "Region": "Mkoa",
            "District": "Wilaya",
            "Select on map": "Chagua kwenye ramani",
            "Gender": "Jinsia",
            "All Genders": "Jinsia Zote",
            "Male": "Mwanaume",
            "Female": "Mwanamke",
            "Age Bracket": "Kundi la Umri",
            "All Ages": "Umri Wote",
            "Apply Filters": "Tumia Vichujio",
            "Reset View": "Weka Upya Mwonekano",
            "Language": "Lugha",
            "Logout": "Toka",
            "Beneficiary": "Mnufaika",
            "Amount": "Kiasi",
            "Enrolled Beneficiaries": "Wanufaika Walioandikishwa",
            "Total Disbursed": "Jumla Iliyolipwa",
            "Budget Allocated": "Bajeti Iliyotengwa",
            "Age Distribution (Count)": "Mgawanyo wa Umri (Idadi)",
            "Age Distribution (Amount)": "Mgawanyo wa Umri (Kiasi)",
            "Gender Distribution (Count)": "Mgawanyo wa Jinsia (Idadi)",
            "Gender Distribution (Amount)": "Mgawanyo wa Jinsia (Kiasi)",
            "Regional Distribution (Count)": "Mgawanyo wa Kieneo (Idadi)",
            "Regional Distribution (Amount)": "Mgawanyo wa Kieneo (Kiasi)",
            "Updating Data...": "Inasasisha data...",
            "No data available": "Hakuna data inayopatikana",
        };
        if (this.isSwahili) {
            return sw[text] || text;
        }
        return text;
    }
}

PBMSDashboard.template = "g2p_pbms_dashboard.PBMSMainLayout";
PBMSDashboard.components = { MapComponent, ChartComponent, KpiComponent };
registry.category("actions").add("pbms_dashboard_main", PBMSDashboard);
