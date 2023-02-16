from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class MainBranch(models.Model):
    _name = "main.branch"
    _description = "This model will help to handel subcity payment"


    name = fields.Char(string="Subcity", defualt='draft', readonly=True)
    amount = fields.Float(string='amount')
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True, )
    time_frame = fields.Many2one('reconciliation.time.fream', string='Time frame',
                                 domain="[('fiscal_year', '=', fiscal_year)]", required=True, )
    payments = fields.One2many('city.payment','main',string='payments')
    amount_2 = fields.Float(string='Amount received')
    amount_3 = fields.Float(string='Diffrence')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('register','Register'),], default='draft', string="Status")
    cash_account_id = fields.Many2one("account.account",
                                      string="Bank Account", domain=[('user_type_id', '=', 'Bank and Cash')])
    income_account_id = fields.Many2one("account.account",
                                        string="Income Account", domain=[('user_type_id', '=', 'Income')])
    journal_id = fields.Many2one('account.journal', 'Journal')
    account_move = fields.Many2one('account.move', string='Account Move')
    date = fields.Date("Date", required=True,
                       default=fields.Date.context_today)
    payment_ref = fields.Char("Payment Ref.")

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('city.payment')
        vals.update({'name': seq})

        return super(MainBranch, self).create(vals)

    @api.onchange('time_frame')
    def _get_lines_2(self):
          if self.time_frame:
            member = self.env['city.payment'].search([('time_frame', '=', self.time_frame.id)])
            val = []
            amount = 0
            for line in member:
               if line.state == 'submit':
                amount = line.amount + amount
                val.append(line.id)
            self.payments = val
            self.amount = amount
            self.amount_3 = self.amount_2 - self.amount

    @api.onchange('payments', 'amount_2')
    def _payment_opnchange(self):
        amount = 0
        for line in self.payments:
            amount = line.amount + amount
        self.amount = amount
        self.amount_3 = self.amount_2 - self.amount

    def set_draft(self):
        for line in self.payments:
            line.state = 'submit'
        self.state = 'draft'

    def set_post(self):
        move_vals = {
            'date': self.date,
            'invoice_date': self.date,
            'type': 'entry',
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'state': 'draft',
            'fiscal_year': self.fiscal_year.id,
            'line_ids': [],

        }
        move_vals['line_ids'].append((0, 0, {
            'name': self.income_account_id.name,
            'debit': 0.0,
            'credit': self.amount_2,
            'account_id': self.income_account_id.id,
            'partner_id': self.env.user.partner_id.id,
            'exclude_from_invoice_tab': False,
        }))

        move_vals['line_ids'].append((0, 0, {
                'name': self.cash_account_id.name,
                'debit': self.amount_2,
                'credit': 0.0,
                'account_id': self.cash_account_id.id,
                'partner_id': self.env.user.partner_id.id,
                'exclude_from_invoice_tab': False,
            }))
        move = self.env['account.move'].sudo().create(move_vals)
        self.account_move = move.id
        self.state = 'register'

    def set_submit(self):
        for line in self.payments:
            line.state = 'register'
        self.state = 'submit'


