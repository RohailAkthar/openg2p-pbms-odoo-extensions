"""Mixin for the themed list searches: exact matches first. Loaded before the models that use it."""
from odoo import api, models


def label_of(record, field_name):
    """Visible label of a selection field's current value."""
    options = dict(record._fields[field_name]._description_selection(record.env))
    return options.get(record[field_name]) or ""


class NsipaExactFirstMixin(models.AbstractModel):
    """List searches that put EXACT matches first: rows where one of the displayed columns equals what was
    typed (ignoring case) come before rows that merely contain it. The rest of the order is unchanged."""

    _name = "nsipa.exact.search.mixin"
    _description = "Search: exact matches first"
    _nsipa_search_fields = ("nsipa_search",)

    def _nsipa_exact_values(self):
        """Displayed column values of this record, as text. Overridden per model."""
        return []

    def _nsipa_search_text(self, domain):
        for leaf in domain or []:
            if isinstance(leaf, (list, tuple)) and len(leaf) == 3 and leaf[0] in self._nsipa_search_fields:
                return (leaf[2] or "").strip() if isinstance(leaf[2], str) else ""
        return ""

    def _nsipa_is_exact(self, text):
        needle = text.lower()
        return any(str(v).strip().lower() == needle for v in self._nsipa_exact_values() if v not in (False, None, ""))

    @api.model
    def web_search_read(self, domain, specification, offset=0, limit=None, order=None, count_limit=None):
        text = self._nsipa_search_text(domain)
        if not text:
            return super().web_search_read(
                domain, specification, offset=offset, limit=limit, order=order, count_limit=count_limit
            )
        records = self.search(domain, order=order)
        ranked = records.sorted(key=lambda r: 0 if r._nsipa_is_exact(text) else 1)  # stable: keeps the base order
        page = ranked[offset: offset + limit] if limit else ranked[offset:]
        return {"length": len(ranked), "records": page.web_read(specification) if page else []}
