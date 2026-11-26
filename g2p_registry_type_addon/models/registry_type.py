from enum import Enum
from odoo import models, fields


class G2PTargetModelMapping:
    """Static mapping from registry type key to model name."""

    MODEL_MAPPING = {
        "student": "g2p.student.registry",
        "farmer": "g2p.farmer.registry",
        "household": "g2p.household.registry",
    }

    # The household registry is read straight from the NSR master register.
    HOUSEHOLD_TABLE = "g2p_register_households"
    # Odoo field name -> real NSR column name, where they differ (the NSR crop
    # columns are capitalised and some contain spaces/brackets).
    HOUSEHOLD_COLUMN_MAP = {
        **{c.lower(): c for c in (
            "Cashew", "Cassava", "Cocoa", "Cocoyam", "Cottons", "Groundnut",
            "Kolanut", "Millet", "Potatoes", "Rice", "Rubber", "Soybeans",
            "Sugarcane", "Tobacco", "Yam",
        )},
        "beans_cowpea": "Beans (Cowpea)",
        "guinea_corn": "Guinea corn",
        "maize_corn": "Maize (Corn)",
        "oil_palm": "Oil Palm",
        "sesame_beniseed": "Sesame (Beniseed)",
    }

    @classmethod
    def finalize_sql(cls, key, sql, only_active=True):
        """Rewrite SQL generated from an Odoo model so it runs on the real
        source table. Only the household registry needs this; other registry
        types are returned unchanged.

        Maps crop column names to the NSR spelling and (for full queries)
        restricts to ACTIVE households. Pass only_active=False for a bare
        WHERE-clause fragment.
        """
        if key != "household" or not sql:
            return sql
        table = cls.HOUSEHOLD_TABLE
        for odoo_name, column in cls.HOUSEHOLD_COLUMN_MAP.items():
            sql = sql.replace('"%s"."%s"' % (table, odoo_name), '"%s"."%s"' % (table, column))
        if only_active:
            active = '"%s"."record_status" = \'ACTIVE\'' % table
            sql = sql + (" AND " if " WHERE " in sql else " WHERE ") + active
        return sql

    @classmethod
    def get_target_model_name(cls, key):
        """Get the model name for a given key."""
        return cls.MODEL_MAPPING.get(key)


class G2PRegistryType(Enum):
    HOUSEHOLD = "household"
    # Legacy members: kept so existing code/records referencing them still
    # resolve, but no longer offered as choices (see selection()).
    FARMER = "farmer"
    STUDENT = "student"
    OTHER = "other"

    @classmethod
    def selection(cls):
        """Return a list of tuples for Odoo selection fields.

        Only the NSR household registry is offered as a target registry.
        """
        return [(cls.HOUSEHOLD.value, "Household")]
