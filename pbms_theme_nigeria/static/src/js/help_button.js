/** @odoo-module **/
import {Component, onMounted, onWillUnmount, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useBus, useService} from "@web/core/utils/hooks";

const GENERIC = {
    title: "This screen",
    intro: "Review the records shown and use the search box to find what you need.",
    steps: [
        "Confirm you are on the right program or record.",
        "Use the search box and the Search button to narrow the list.",
        "Open a record to see its details before taking any action.",
    ],
};

// Help text per screen, keyed by the menu / page name.
const HELP = {
    "approvals": {
        title: "Approvals",
        intro: "Review enrollment and disbursement lists waiting for your approval, and the approvals you have actioned.",
        steps: [
            "Open View Details on a queued item and check the list, its statistics and beneficiaries.",
            "Approve or Reject, and give a reason. The decision is recorded in the approval history.",
            "Use Approval History to review what you have already actioned.",
        ],
    },
    "programs": {
        title: "Programs",
        intro: "Configure a program and its enrollment, verification and benefit settings.",
        steps: [
            "Open the program and check its identifier and target registry.",
            "Review enrollment settings, verification requirements and linked benefits.",
            "Save authorised changes and confirm the displayed configuration before starting processing.",
        ],
    },
    "enrolment cycles": {
        title: "Enrollment cycles",
        intro: "Track enrollment windows and approvals for each program.",
        steps: [
            "Confirm the program and its current cycle.",
            "Use Create New Cycle to start a cycle, or View to open the program's cycles.",
            "Inside a cycle, create an enrolment list and follow it through approval.",
        ],
    },
    "disbursement cycles": {
        title: "Disbursement cycles",
        intro: "Review program payment cycles and their approval state.",
        steps: [
            "Confirm the program and cycle identifier.",
            "Open the linked beneficiary lists and check entitlement calculations and verification requirements.",
            "Use the approval workflow only when the calculation and required verification are complete.",
        ],
    },
    "transfer types": {
        title: "Transfer types",
        intro: "Manage the transfer types used by programs.",
        steps: [
            "Use + Create transfer type to add a transfer type, or Edit to change one.",
            "Choose the benefit type; cash types need a measurement unit (currency).",
            "Transfer types must exist before they can be added to a program.",
        ],
    },
    "sponsor banks": {
        title: "Sponsor banks",
        intro: "Manage the sponsor banks used for disbursements.",
        steps: [
            "Use + Create sponsor bank to add a bank, or Edit to change one.",
            "Add the administrator details and the program transfer types the bank serves.",
            "Check the bank is linked to the correct program before disbursing.",
        ],
    },
    "master data": {
        title: "Master data",
        intro: "Reference data used across programs: sponsor banks and transfer types.",
        steps: ["Pick Sponsor Banks or Transfer Types from the menu.", "Create or edit entries before using them in a program."],
    },
    "cycle detail": {
        title: "Cycle detail",
        intro: "Review one cycle: its list, workflow state, statistics, beneficiaries and approval history.",
        steps: [
            "Check the Cycle, Workflow and Beneficiaries cards at the top.",
            "Use Create New List when a new version is allowed, or Approve / Reject when it is your turn.",
            "Use the tabs to review statistics, beneficiaries and history before deciding.",
        ],
    },
};

// Optional link for "Ask local AI about this stage"; the link is hidden while this is empty.
const AI_HELP_URL = "";

// Which Knowledge guide (pbms_knowledge) each screen / page title opens. Keys are lower-case.
const GUIDE_FOR = {
    "approvals": "use-approval-queue",
    "approval queue": "use-approval-queue",
    "approval history": "approval-history",
    "programs": "create-program",
    "enrolment cycles": "enrolment-overview",
    "enrollment cycles": "enrolment-overview",
    "enrollment cycle": "enrolment-overview",
    "disbursement cycles": "disbursement-overview",
    "disbursement cycle": "disbursement-overview",
    "transfer types": "create-benefit-code",
    "sponsor banks": "create-sponsor-bank",
    "master data": "setup-checklist",
    "cycle detail": "end-to-end-workflow",
};
const DEFAULT_GUIDE = "what-is-pbms";
// The Programs menu is shown as "Program Management"; Help and guides are looked up by menu name.
GUIDE_FOR["program management"] = GUIDE_FOR["programs"];
HELP["program management"] = HELP["programs"];

const COMMON = {
    need: "An authorised PBMS staff account and the correct program or record reference. Available actions depend on your assigned permissions.",
    next: "Confirm the status or saved values shown by PBMS before continuing. For payment reports, confirm the returned settlement state separately from dispatch.",
    issues: "If data is missing, check the current filters and program selection, then refresh. Resolve displayed validation errors before retrying. If access is denied or processing remains failed, contact the PBMS administrator with the record reference and error message.",
};

// Controller we came from when the Knowledge library was opened from Help / an (i) icon.
let returnTo = null;

class NsipaHelp extends Component {
    static template = "pbms_theme_nigeria.NsipaHelp";
    static props = {};

    setup() {
        this.menus = useService("menu");
        this.router = useService("router");
        this.action = useService("action");
        this.state = useState({open: false, help: GENERIC, name: "", browse: false});
        // Re-render when the screen changes so the button can switch between Help and Back.
        useBus(this.env.bus, "ACTION_MANAGER:UI-UPDATED", () => this.render());
        // The (i) icon next to every page title opens the matching Knowledge guide.
        this._onInfoClick = (ev) => {
            // The (i) in a popup title ("New program" etc.) is drawn by CSS (::after), so it is not a real
            // element: a click on the title bar counts as a click on the icon when it lands just right of the
            // title text, where the icon is drawn (14px gap, 24px wide).
            const modalTitle = ev.target.closest && ev.target.closest(".modal-header .modal-title");
            if (modalTitle) {
                const content = modalTitle.closest(".modal-content");
                if (content && content.querySelector(".nsipa_prog_popup")) {
                    const range = document.createRange();
                    range.selectNodeContents(modalTitle);
                    const text = range.getBoundingClientRect();
                    const box = modalTitle.getBoundingClientRect();
                    const onIcon =
                        ev.clientX >= text.right &&
                        ev.clientX <= text.right + 14 + 24 + 8 &&
                        ev.clientY >= box.top &&
                        ev.clientY <= box.bottom;
                    if (onIcon) {
                        const name = (modalTitle.textContent || "").trim().toLowerCase();
                        let guide = GUIDE_FOR[this._screen()] || DEFAULT_GUIDE;
                        if (name.includes("transfer type")) {
                            guide = "create-benefit-code";
                        } else if (name.includes("sponsor bank")) {
                            guide = "create-sponsor-bank";
                        } else if (name.includes("program")) {
                            guide = "create-program";
                        }
                        this.openKnowledge(guide);
                    }
                }
                return;
            }
            const icon = ev.target.closest && ev.target.closest(".nsipa_info_icon");
            if (!icon) {
                return;
            }
            const h1 = icon.closest("h1");
            const title = ((h1 && h1.textContent) || "").replace(/\bi\s*$/, "").trim().toLowerCase();
            this.openKnowledge(GUIDE_FOR[title] || GUIDE_FOR[this._screen()] || DEFAULT_GUIDE);
        };
        onMounted(() => document.addEventListener("click", this._onInfoClick));
        onWillUnmount(() => document.removeEventListener("click", this._onInfoClick));
    }

    // Opens the Knowledge library (module pbms_knowledge) at a guide. Falls back to the
    // in-page help panel when that module is not installed.
    openKnowledge(guide) {
        if (registry.category("actions").contains("pbms_knowledge")) {
            this.state.open = false;
            const current = this.action.currentController;
            if (current && !(current.action && current.action.tag === "pbms_knowledge")) {
                returnTo = current.jsId;
            }
            this.action.doAction({
                type: "ir.actions.client",
                tag: "pbms_knowledge",
                name: "Knowledge",
                params: {guide: guide || DEFAULT_GUIDE},
            });
        } else {
            this.state.open = true;
        }
    }

    get inKnowledge() {
        const c = this.action.currentController;
        return !!(c && c.action && c.action.tag === "pbms_knowledge");
    }

    // Back from the Knowledge library to the screen the user came from.
    async goBack() {
        if (returnTo) {
            try {
                await this.action.restore(returnTo);
                returnTo = null;
                return;
            } catch (e) {
                returnTo = null;
            }
        }
        window.history.back();
    }

    openCurrentGuide() {
        this.openKnowledge(GUIDE_FOR[this._screen()] || DEFAULT_GUIDE);
    }

    _screen() {
        const hash = this.router.current.hash || {};
        if (hash.model === "g2p.bgtask.summary.wizard") {
            return "cycle detail";
        }
        const menu = hash.menu_id ? this.menus.getMenu(hash.menu_id) : null;
        return ((menu && menu.name) || "").trim().toLowerCase();
    }

    toggle() {
        if (!this.state.open) {
            const key = this._screen();
            const help = HELP[key] || GENERIC;
            this.state.help = help;
            this.state.name = help.title;
        }
        this.state.open = !this.state.open;
        this.state.browse = false;
    }

    toggleBrowse() {
        this.state.browse = !this.state.browse;
    }

    get allHelp() {
        return Object.values(HELP);
    }

    showHelp(help) {
        this.state.help = help;
        this.state.name = help.title;
    }

    get aiUrl() {
        return AI_HELP_URL;
    }

    get common() {
        return COMMON;
    }
}

registry.category("main_components").add("pbms_theme_nigeria.NsipaHelp", {Component: NsipaHelp});
