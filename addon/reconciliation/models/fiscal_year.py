from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.addons import decimal_precision as dp
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError, ValidationError

import logging


class ReconciliationTimeFream(models.Model):
    _name = "fiscal.year"
    _description = "fiscal year"

    name = fields.Char('Description', size=256)
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    fiscal_year = fields.Many2one('fiscal.year', string="Last Fiscal year")
    close = fields.Many2one('account.move', string="close Entry", ondelete='restrict', copy=False, readonly=True)
    open = fields.Many2one('account.move', string="opening Entry", ondelete='restrict', copy=False, readonly=True)
    state = fields.Selection([
        ('draft', 'New'),
        ('active', 'Active'),
        ('locked', 'Locked'),
        ('closed', 'Closed')], default='draft', string="Status")


    def activate(self):
        years = self.env['fiscal.year'].search([])
        for year in years:
            if year.state == 'active':
                raise ValidationError(_('There active fiscal year'))
        self.state = 'active'

    def lock(self):
        self.state = 'locked'

    def close(self):
        print("close")

    def set_new(self):
        self.state = 'draft'
