from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    fund_line = fields.One2many('fund.lines', 'fund_analytic_account_id', 'Fund Lines')

