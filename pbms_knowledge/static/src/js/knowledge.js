/** @odoo-module **/
import {Component, useState} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {CATEGORIES, GUIDES} from "./guides_data";

class PbmsKnowledge extends Component {
    static template = "pbms_knowledge.Knowledge";
    static props = ["*"];

    setup() {
        this.router = useService("router");
        const hash = this.router.current.hash || {};
        // A guide can be requested by action params (Help button / (i) icons) or by the URL (&guide=...).
        const params = (this.props.action && this.props.action.params) || {};
        const first = GUIDES.find((g) => g.id === (params.guide || hash.guide)) || null;
        this.state = useState({
            query: "",
            guideId: first ? first.id : null,
            collapsed: {},
            copied: false,
        });
    }

    get categories() {
        return CATEGORIES;
    }

    get guide() {
        return GUIDES.find((g) => g.id === this.state.guideId) || null;
    }

    get category() {
        const g = this.guide;
        return g ? CATEGORIES.find((c) => c.id === g.category) : null;
    }

    get filtered() {
        const q = this.state.query.trim().toLowerCase();
        if (!q) {
            return GUIDES;
        }
        return GUIDES.filter((g) => {
            const hay = [
                g.title,
                g.summary,
                g.roles,
                ...g.steps.map((s) => s.t + " " + s.d),
                ...(g.issues || []),
            ]
                .join(" ")
                .toLowerCase();
            return q.split(/\s+/).every((w) => hay.includes(w));
        });
    }

    guidesOf(cat) {
        return this.filtered.filter((g) => g.category === cat.id);
    }

    get searching() {
        return this.state.query.trim().length > 0;
    }

    get related() {
        const g = this.guide;
        return g ? (g.related || []).map((id) => GUIDES.find((x) => x.id === id)).filter(Boolean) : [];
    }

    get neighbours() {
        const g = this.guide;
        if (!g) {
            return {prev: null, next: null};
        }
        const i = GUIDES.indexOf(g);
        return {prev: GUIDES[i - 1] || null, next: GUIDES[i + 1] || null};
    }

    countOf(cat) {
        return GUIDES.filter((g) => g.category === cat.id).length;
    }

    open(id) {
        this.state.guideId = id;
        this.state.copied = false;
        this.router.pushState({guide: id});
        const body = document.querySelector(".pbk_main");
        if (body) {
            body.scrollTop = 0;
        }
    }

    home() {
        this.state.guideId = null;
        this.router.pushState({guide: undefined});
    }

    toggleCat(cat) {
        this.state.collapsed[cat.id] = !this.state.collapsed[cat.id];
    }

    async copyLink() {
        try {
            await navigator.clipboard.writeText(window.location.href);
            this.state.copied = true;
        } catch (e) {
            this.state.copied = false;
        }
    }

    print() {
        window.print();
    }
}

registry.category("actions").add("pbms_knowledge", PbmsKnowledge);
