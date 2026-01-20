import logging
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

from .registry import G2PRegistry

class ResPartner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(translate=False)
    birthdate = fields.Date("Date of Birth")
    age = fields.Integer(string="Age", compute="_compute_age", store=False, readonly=True,search=False)
    gender = fields.Selection(
        selection=[("male", "Male"), ("female", "Female")], string="Gender"
    )

    @api.depends("birthdate")
    def _compute_age(self):
        for record in self:
            if record.birthdate:
                now = fields.Date.today()
                delta = relativedelta(now, record.birthdate)
                record.age = delta.years
            else:
                record.age = 0

    @api.onchange("birthdate")
    def _birthdate_onchange(self):
        """
        This function are used to raise a validation error in case the
        birthdate date is being set greater than the date today
        """
        for rec in self:
            if rec.birthdate and rec.birthdate > fields.Date.today():
                raise ValidationError(_("You can't select a date of birth greater than today"))

