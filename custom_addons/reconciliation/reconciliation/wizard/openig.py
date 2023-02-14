from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class FinancialOpening(models.TransientModel):
    _name = "financial.opening"


    journal_id = fields.Many2one('account.journal', 'Journal', required=True)
    date = fields.Date('Current Date')
    debit = fields.Many2many('account.account.type', string="Debit Account group")
    credit = fields.Many2many('account.account.type','write_date', string="Credit Account group")
    diff = fields.Many2one('account.account', string="difference")



    def open_year(self):
        active_id = self.env.context.get('active_ids', [])
        id = active_id[0]
        date = self.date
        year = self.env['fiscal.year'].search([("id", "=", id)])
        active_time_frame = self.env['reconciliation.time.fream'].search(
            [('date_from', '<=', date), ('date_to', '>=', date)], limit=1)
        # print("active_time_frame", active_time_frame.id)
        account = self.env['account.move.line'].search([("fiscal_year", "=", year.fiscal_year.id)])
        account_2 = self.env['account.move'].search([("fiscal_year", "=", year.fiscal_year.id)])

        if not active_time_frame.id:
            # print("date", active_time_frame.id)
            raise ValidationError(_(
                'please set Time frame for the journal'))
        # for line in account_2:


        move_vals = {
            'date': date,
            'invoice_date': datetime.today(),
            'type': 'entry',
            'time_frame': active_time_frame.id,
            'ref': "opening entry",
            'journal_id': self.journal_id.id,
            'fiscal_year': id,
            'state': 'draft',
            'line_ids': [],

        }
        tot_debit = 0
        tot_credit = 0
        for group in self.credit:
            account = self.env['account.account'].search([("user_type_id", "=", group.id)])
            for acc in account:
                total_debit = 0
                total_credit = 0
                line = self.env['account.move.line'].search([('account_id', '=', acc.id), ("fiscal_year", "=", id)])
                for tran in line:
                    total_debit = total_debit + tran.debit
                    total_credit = total_credit + tran.credit
                acc.account_debit = total_debit
                acc.account_credit = total_credit
                acc.account_balance = acc.account_debit - acc.account_credit
                tot_credit = tot_credit + acc.account_balance
                move_vals['line_ids'].append((0, 0, {
                    'name': acc.name,
                    'debit': abs(acc.account_balance),
                    'credit': 0.0,
                    'account_id': acc.id,
                    'fiscal_year': id,
                    'exclude_from_invoice_tab': False,
                }))

        for group in self.debit:
            account = self.env['account.account'].search([("user_type_id", "=", group.id)])
            # print("db account", account)
            for acc in account:
                total_debit = 0
                total_credit = 0
                line = self.env['account.move.line'].search([('account_id', '=', acc.id), ("fiscal_year", "=", id)])
                for tran in line:
                    total_debit = total_debit + tran.debit
                    total_credit = total_credit + tran.credit
                acc.account_debit = total_debit
                acc.account_credit = total_credit
                acc.account_balance = acc.account_debit - acc.account_credit
                # print("db acc.name", acc.name, "acc.account_balance", acc.account_balance)
                # print("per tot_debit", tot_debit)
                tot_debit = tot_debit + abs(acc.account_balance)
                # print("tot_debit after", tot_debit)
                move_vals['line_ids'].append((0, 0, {
                    'name': acc.name,
                    'debit': 0,
                    'credit': abs(acc.account_balance),
                    'account_id': acc.id,
                    'fiscal_year': id,
                    'exclude_from_invoice_tab': False,
                }))

        # print("tot_debit", tot_debit, "tot_credit", tot_credit)
        if tot_debit < tot_credit:
            move_vals['line_ids'].append((0, 0, {
                'name': self.diff.name,
                'debit': 0,
                'credit': abs(tot_debit - tot_credit),
                'account_id': self.diff.id,
                'fiscal_year': id,
                'exclude_from_invoice_tab': False,
            }))
        else:
            move_vals['line_ids'].append((0, 0, {
                'name': self.diff.name,
                'debit': abs(tot_debit - tot_credit),
                'credit': 0,
                'account_id': self.diff.id,
                'fiscal_year': id,
                'exclude_from_invoice_tab': False,
            }))
        year.state = 'active'
        # print(move_vals)
        move = self.env['account.move'].sudo().create(move_vals)
        year.open = move.id
