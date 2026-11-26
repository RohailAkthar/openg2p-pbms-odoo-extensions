from datetime import datetime, timedelta

from odoo import fields, models

from .nsipa_exact_mixin import label_of


class G2PProgramDefinition(models.Model):
    _name = "g2p.program.definition"
    _inherit = ["g2p.program.definition", "nsipa.exact.search.mixin"]
    _nsipa_search_fields = ("nsipa_search", "nsipa_cycle_search", "nsipa_dcycle_search")

    def _nsipa_exact_values(self):
        self.ensure_one()
        return [
            self.program_mnemonic, self.description, label_of(self, "target_registry"), label_of(self, "program_status"),
            self.latest_ec_cycle_name, self.latest_ec_version, self.latest_ec_stage, label_of(self, "latest_ec_status"),
            label_of(self, "enrollment_frequency"),
            self.latest_dc_cycle_name, self.latest_dc_version, self.latest_dc_stage, label_of(self, "latest_dc_status"),
        ]

    # Search-only helper for the list's search bar: one entry that looks in every column of the list.
    nsipa_search = fields.Char(string="Programs", compute="_compute_nsipa_search", search="_search_nsipa_search")

    def _compute_nsipa_search(self):
        for rec in self:
            rec.nsipa_search = False

    def _search_nsipa_search(self, operator, value):
        text = (value or "").strip()
        if not text:
            return []
        needle = text.lower()

        def matching_keys(field_name):
            # Match what the user sees (the label) as well as the stored key.
            options = self._fields[field_name]._description_selection(self.env)
            return [key for key, label in options if needle in (label or "").lower() or needle in str(key).lower()]

        return [
            "|", "|", "|",
            ("program_mnemonic", "ilike", text),
            ("description", "ilike", text),
            ("target_registry", "in", matching_keys("target_registry")),
            ("program_status", "in", matching_keys("program_status")),
        ]

    # Search-only helpers for the Enrollment / Disbursement cycles lists: one entry that looks in every column
    # shown there. The "latest cycle" columns are computed (not searchable), so the cycles themselves are
    # searched and a program matches when its LATEST cycle matches (or its own name / frequency does).
    nsipa_cycle_search = fields.Char(
        string="Enrollment cycles", compute="_compute_nsipa_search", search="_search_nsipa_cycle_search"
    )
    nsipa_dcycle_search = fields.Char(
        string="Disbursement cycles", compute="_compute_nsipa_search", search="_search_nsipa_dcycle_search"
    )

    def _search_nsipa_cycle_search(self, operator, value):
        return self._nsipa_latest_cycle_domain(value, "g2p.enrollment.cycle", "enrollment_frequency")

    def _search_nsipa_dcycle_search(self, operator, value):
        return self._nsipa_latest_cycle_domain(value, "g2p.disbursement.cycle", None)

    def _nsipa_latest_cycle_domain(self, value, cycle_model, frequency_field):
        text = (value or "").strip()
        if not text:
            return []
        needle = text.lower()
        Cycle = self.env[cycle_model]

        def matching_keys(model, field_name):
            options = model._fields[field_name]._description_selection(self.env)
            return [key for key, label in options if needle in (label or "").lower() or needle in str(key).lower()]

        # Cycle columns: Current Cycle, Current List #, Current Stage, Current Status, Cycle Created On.
        terms = [
            [("cycle_name", "ilike", text)],
            [("current_list_id.mnemonic", "ilike", text)],
            [("current_stage_display", "ilike", text)],
            [("current_approval_status", "in", matching_keys(Cycle, "current_approval_status"))],
        ]
        # Cycle Created On: accept YYYY, YYYY-MM or YYYY-MM-DD as typed.
        parts = text.split("-")
        if len(parts) <= 3 and all(p.isdigit() for p in parts) and len(parts[0]) == 4:
            try:
                year = int(parts[0])
                month = int(parts[1]) if len(parts) > 1 else None
                day = int(parts[2]) if len(parts) > 2 else None
                start = datetime(year, month or 1, day or 1)
                if day:
                    end = start + timedelta(days=1)
                elif month:
                    end = datetime(year + (month == 12), (month % 12) + 1, 1)
                else:
                    end = datetime(year + 1, 1, 1)
                terms.append(["&", ("creation_date", ">=", start), ("creation_date", "<", end)])
            except ValueError:
                pass
        cycle_domain = ["|"] * (len(terms) - 1)
        for term in terms:
            cycle_domain += term
        matching = Cycle.search(cycle_domain)
        program_ids = set()
        for program in matching.mapped("program_id"):
            latest = Cycle.search([("program_id", "=", program.id)], order="cycle_number desc", limit=1)
            if latest in matching:
                program_ids.add(program.id)

        domain = [("program_mnemonic", "ilike", text), ("id", "in", list(program_ids))]
        if frequency_field:
            domain.append((frequency_field, "in", matching_keys(self, frequency_field)))
        return ["|"] * (len(domain) - 1) + domain

    def action_open_edit(self):
        """Presentation only: the themed Programs list asks for the popup form (context nsipa_popup).
        Program Operations (management mode) and every other caller keep the original full-page form."""
        ctx = self.env.context
        if not ctx.get("nsipa_popup") or ctx.get("program_view_mode", "config") != "config":
            return super().action_open_edit()
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Edit program",
            "res_model": "g2p.program.definition",
            "res_id": self.id,
            "view_mode": "form",
            "views": [[self.env.ref("pbms_theme_nigeria.view_g2p_programs_new_popup_form").id, "form"]],
            "target": "new",
            "context": {
                "create": False,
                "program_form_edit": True,
                "program_form_create": False,
                "program_view_mode": "config",
                "dialog_size": "extra-large",
            },
        }
