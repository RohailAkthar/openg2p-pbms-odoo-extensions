import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

SQL_TYPE_MAP = {
    'integer': fields.Integer,
    'bigint': fields.Integer,
    'smallint': fields.Integer,
    'numeric': fields.Float,
    'real': fields.Float,
    'double precision': fields.Float,
    'boolean': fields.Boolean,
    'date': fields.Date,
    'timestamp with time zone': fields.Datetime,
    'timestamp without time zone': fields.Datetime,
    'character varying': fields.Char,
    'text': fields.Char,
    'json': fields.Char,
    'jsonb': fields.Char,
}


class G2PRegistry(models.AbstractModel):
    _name = "g2p.registry"
    _description = "Abstract G2P Registry"

    internal_record_id = fields.Char(string="Internal Record ID")

    def action_open_view(self):
        return {
            "type": "ir.actions.act_window",
            "name": "View Registry Record",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
            "flags": {"mode": "readonly"},
        }

    @api.model
    def _register_hook(self):
        super()._register_hook()
        self._introspect_dynamic_columns()

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        self._introspect_dynamic_columns()
        return super().fields_get(allfields=allfields, attributes=attributes)

    @api.model
    def _introspect_dynamic_columns(self):
        """
        Dynamically introspects the PostgreSQL table for any columns that are
        not yet explicitly defined on this model, and registers them on the fly.
        Ensures any new column added to the NSR table is immediately available
        in the Domain Builder without changing Python code.
        """
        if not getattr(self, '_table', None) or self._abstract:
            return
        try:
            self.env.cr.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
                """,
                (self._table,)
            )
            rows = self.env.cr.fetchall()
            cls = type(self)
            for col_name, data_type in rows:
                if col_name in cls._fields:
                    continue
                field_cls = SQL_TYPE_MAP.get(data_type, fields.Char)
                label = col_name.replace('_', ' ').title()
                field = field_cls(string=label)
                field._setup_attrs(cls, col_name)
                cls._fields[col_name] = field
                _logger.info("Dynamic registry field registered: %s.%s (%s)", self._name, col_name, field_cls.__name__)
        except Exception as e:
            _logger.warning("Dynamic column introspection failed for %s: %s", self._name, e)
