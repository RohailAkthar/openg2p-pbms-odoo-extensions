"""Presentation helpers: one search-bar entry per list that matches every column the list shows.

Each model gets a non-stored, search-only Char field; the list's search view uses it, so typing in the themed
search box looks in all columns (including selection labels, numbers and dates as typed).
"""
from datetime import datetime, timedelta

from odoo import fields, models

from .nsipa_exact_mixin import label_of


def selection_keys(model, field_name, text):
    """Keys of a selection field whose key or visible label contains the text."""
    needle = text.lower()
    options = model._fields[field_name]._description_selection(model.env)
    return [key for key, label in options if needle in (label or "").lower() or needle in str(key).lower()]


def date_terms(field_name, text):
    """Domain terms for a datetime column when the text is YYYY, YYYY-MM or YYYY-MM-DD (else [])."""
    parts = text.split("-")
    if not (len(parts) <= 3 and all(p.isdigit() for p in parts) and len(parts[0]) == 4):
        return []
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
    except ValueError:
        return []
    return ["&", (field_name, ">=", start), (field_name, "<", end)]


def any_of(groups):
    """OR together groups (each a list of domain terms in prefix notation)."""
    groups = [g for g in groups if g]
    domain = ["|"] * (len(groups) - 1)
    for group in groups:
        domain += group
    return domain or [("id", "=", 0)]


class G2PBenefitCodes(models.Model):
    _name = "g2p.benefit.codes"
    _inherit = ["g2p.benefit.codes", "nsipa.exact.search.mixin"]

    def _nsipa_exact_values(self):
        self.ensure_one()
        return [self.benefit_mnemonic, label_of(self, "benefit_type"), self.measurement_unit, self.benefit_description]

    nsipa_search = fields.Char(string="Benefit codes", compute="_compute_nsipa_search", search="_search_nsipa_search")

    def _compute_nsipa_search(self):
        for rec in self:
            rec.nsipa_search = False

    def _search_nsipa_search(self, operator, value):
        text = (value or "").strip()
        if not text:
            return []
        return any_of([
            [("benefit_mnemonic", "ilike", text)],
            [("benefit_type", "in", selection_keys(self, "benefit_type", text))],
            [("measurement_unit", "ilike", text)],
            [("benefit_description", "ilike", text)],
        ])


class G2PWorkflowPendingStage(models.Model):
    _name = "g2p.workflow.pending.stage"
    _inherit = ["g2p.workflow.pending.stage", "nsipa.exact.search.mixin"]

    def _nsipa_exact_values(self):
        self.ensure_one()
        return [
            self.program_mnemonic, self.cycle_name, label_of(self, "list_stage"), self.current_stage_name,
            self.list_number, self.number_of_registrants,
        ]

    nsipa_search = fields.Char(string="Approvals", compute="_compute_nsipa_search", search="_search_nsipa_search")

    def _compute_nsipa_search(self):
        for rec in self:
            rec.nsipa_search = False

    def _search_nsipa_search(self, operator, value):
        text = (value or "").strip()
        if not text:
            return []
        groups = [
            [("list_id.program_id.program_mnemonic", "ilike", text)],                      # Program
            ["|", ("list_id.enrollment_cycle_id.cycle_name", "ilike", text),
             ("list_id.disbursement_cycle_id.cycle_name", "ilike", text)],                  # Cycle #
            [("list_id.list_stage", "in", selection_keys(self.env["g2p.beneficiary.list"], "list_stage", text))],  # Type
            [("current_stage_id.stage_name", "ilike", text)],                              # Current Stage
            date_terms("enqueued_at", text),                                               # Queued Date
        ]
        if text.isdigit():
            groups.append([("list_id.list_number", "=", int(text))])                        # List #
            groups.append([("list_id.number_of_registrants", "=", int(text))])              # # of Beneficiaries
        return any_of(groups)


class G2PWorkflowStageHistory(models.Model):
    _name = "g2p.workflow.stage.history"
    _inherit = ["g2p.workflow.stage.history", "nsipa.exact.search.mixin"]

    def _nsipa_exact_values(self):
        self.ensure_one()
        return [
            label_of(self, "list_type"), self.stage_name, self.stage_number, label_of(self, "status"),
            self.acted_by.name,
        ]

    nsipa_search = fields.Char(string="Approval history", compute="_compute_nsipa_search", search="_search_nsipa_search")

    def _compute_nsipa_search(self):
        for rec in self:
            rec.nsipa_search = False

    def _search_nsipa_search(self, operator, value):
        text = (value or "").strip()
        if not text:
            return []
        groups = [
            [("list_type", "in", selection_keys(self, "list_type", text))],     # Type
            [("stage_name", "ilike", text)],                                     # Stage
            [("status", "in", selection_keys(self, "status", text))],           # Status
            [("acted_by.name", "ilike", text)],                                  # Acted By
            date_terms("enqueued_at", text),                                     # Enqueued At
            date_terms("acted_at", text),                                        # Acted On
        ]
        if text.isdigit():
            groups.append([("stage_number", "=", int(text))])                    # Stage #
        return any_of(groups)


class G2PWarehouse(models.Model):
    _name = "g2p.warehouse"
    _inherit = ["g2p.warehouse", "nsipa.exact.search.mixin"]

    nsipa_search = fields.Char(string="Sponsor banks", compute="_compute_nsipa_search", search="_search_nsipa_search")

    def _compute_nsipa_search(self):
        for rec in self:
            rec.nsipa_search = False

    def _search_nsipa_search(self, operator, value):
        text = (value or "").strip()
        if not text:
            return []
        return any_of([[("name", "ilike", text)], [("warehouse_mnemonic", "ilike", text)]])

    def _nsipa_exact_values(self):
        self.ensure_one()
        return [self.name, self.warehouse_mnemonic]
