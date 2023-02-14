# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.misc import formatLang


class AccountAccount(models.Model):
    _inherit = 'account.account'

    account_debit = fields.Float('Account Debit', readonly=True)
    account_credit = fields.Float('Account Credit', readonly=True)
    account_balance = fields.Float('Account Credit', readonly=True)
