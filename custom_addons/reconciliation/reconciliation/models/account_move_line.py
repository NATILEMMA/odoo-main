# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from datetime import datetime

class AccountMove(models.Model):
    _inherit = "account.move"

    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True,)
    time_frame = fields.Many2one('reconciliation.time.fream', string='Time frame', domain= "[('fiscal_year', '=', fiscal_year)]", required=True,)

    @api.model
    def default_get(self, fields):
        date = self.date
        if not date:
            date = datetime.now()
        # print('date2', date)
        active_time_frame = self.env['reconciliation.time.fream'].search(
            [('date_from', '<=', date),('date_to', '>=', date)],limit=1)
        if not active_time_frame.id:
            raise ValidationError(_(
                'please set Time frame for the journal'))
        active_fiscal_year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
        if not active_fiscal_year.id:
            raise ValidationError(_(
                'please set Active fiscal year for the journal'))
        self.time_frame = active_time_frame.id
        self.fiscal_year = active_fiscal_year.id
        return super(AccountMove, self).default_get(fields)


    @api.onchange('time_frame')
    def onchange_time_frame(self):
          if self.time_frame:
            if not (self.time_frame.date_from <= self.date and self.time_frame.date_to >= self.date):
                raise AccessError(_("You Date is not in this time frame."))
            for line in self.line_ids:
                   line.time_frame = self.time_frame
          if self.fiscal_year:
              for line in self.line_ids:
                  line.fiscal_year = self.fiscal_year


    def post(self):
        flag = self.env['res.users'].has_group('account.group_account_manager')
        if not flag:
            if self.fiscal_year.state != 'active':
                raise AccessError(_("You Posting date out of the active fiscal year."))
        active_time_frame = self.env['reconciliation.time.fream'].search(
            [('is_active', '=', True)])
        active = 0
        for line in active_time_frame:
          if self.date:
            if line.date_from <= self.date and line.date_to >= self.date:
                active = active + 1
        if active == 0:
          if self.date:
            raise AccessError(_("You Posting date out of the current time frame."))
        for line in self.line_ids:
            line.fiscal_year = self.fiscal_year.id
            line.time_frame = self.time_frame.id
        return super(AccountMove, self).post()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    bank_statement_id = fields.Many2one('bank.reconciliation', 'Bank Statement', copy=False)
    statement_date = fields.Date('Bank.St Date', copy=False)
    reconciled = fields.Boolean('Is reconciled')
    is_reconciled = fields.Boolean('Is reconciled')
    is_done = fields.Boolean('Is done')
    time_frame = fields.Many2one('reconciliation.time.fream', 'Time frame', required=True)
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True)

    # def write(self, vals):
    #     if not vals.get("statement_date"):
    #         vals.update({"reconciled": False})
    #         for record in self:
    #             if record.payment_id and record.payment_id.state == 'reconciled':
    #                 record.payment_id.state = 'posted'
    #     elif vals.get("statement_date"):
    #         vals.update({"reconciled": True})
    #         for record in self:
    #             if record.payment_id:
    #                 record.payment_id.state = 'reconciled'
    #     res = super(AccountMoveLine, self).write(vals)
    #     return res

    @api.model
    def default_get(self, fields):
        if self.fiscal_year and self.time_frame:
            date = self.date
            if not date:
                date = datetime.now()
            active_time_frame = self.env['reconciliation.time.fream'].search(
                [('date_from', '<=', date), ('date_to', '>=', date)], limit=1)
            if not active_time_frame.id:
                raise ValidationError(_(
                    'please set Time frame for the journal line'))
            active_fiscal_year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)

            if not active_fiscal_year.id:
                raise ValidationError(_(
                    'please set Active fiscal year for the journal'))
            self.time_frame = active_time_frame.id
            self.fiscal_year = active_fiscal_year.id
        return super(AccountMoveLine, self).default_get(fields)