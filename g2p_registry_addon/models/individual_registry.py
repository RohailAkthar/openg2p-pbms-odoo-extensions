import logging
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

from .registry import G2PRegistry

class G2PIndividualRegistry(models.Model):
    _name = "g2p.individual.registry"
    _description = "Individual Registry"
    _inherit = "g2p.registry"

    family_name = fields.Char(translate=False)
    given_name = fields.Char(translate=False)
    birthdate = fields.Date("Date of Birth")
    age = fields.Integer(string="Age", compute="_compute_calc_age", store=True, readonly=True)
    gender = fields.Selection(
        selection=[("male", "Male"), ("female", "Female")], string="Gender"
    )

    @api.depends("birthdate")
    def _compute_calc_age(self):
        for line in self:
            if line.birthdate:
                now = fields.Date.today()
                delta = relativedelta(now, line.birthdate)
                line.age = delta.years
            else:
                line.age = 0

    @api.onchange("birthdate")
    def _birthdate_onchange(self):
        """
        This function are used to raise a validation error in case the
        birthdate date is being set greater than the date today
        """
        for rec in self:
            if rec.birthdate and rec.birthdate > fields.date.today():
                raise ValidationError(_("You can't select a date of birth greater than today"))
    @api.model
    def _cron_update_age(self):
        _logger.info("Updating age for all individuals")
        individuals = self.search([("birthdate", "!=", False)])
        individuals._compute_calc_age()