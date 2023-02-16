# ©  2020 Deltatech
# See README.rst file on addons root folder for license details
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import datetime


class SubCityWizard(models.TransientModel):
    _name = "sub.city.wizard"
    _description = "Register Payment sub city Wizard"

    amount = fields.Float(string='Amount')
    amount_2 = fields.Float(string='Amount received')
    amount_3 = fields.Float(string='Diffrence')
    ref = fields.Char(string='Reference')
    pull = fields.Boolean(string='Get all payment on this month')
    date = fields.Date(string='Deposit Date', default=datetime.today())
    payments = fields.Many2many('sub.payment', string='payments')
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True, )
    time_frame = fields.Many2one('reconciliation.time.fream', string='Time frame',
                                 domain="[('fiscal_year', '=', fiscal_year)]", required=True, )
    name = fields.Many2one('membership.handlers.parent', string="Subcity", required=True)


    @api.model
    def default_get(self, fields):
        res = super(SubCityWizard, self).default_get(fields)
        active_fiscal_year = self.env['fiscal.year'].search([('state', '=', 'active')], limit=1)
        active_ids = self.env.context.get("active_ids")
        line_2 = []
        total = 0
        for line in active_ids:
            line_2.append(line)
            id = line
            time_frame = self.env['sub.payment'].search([('id', '=', id)], limit=1)
            total = time_frame.amount + total

        res.update({
                    "payments": [(6, 0, line_2)],
                    "fiscal_year": active_fiscal_year.id,
                    "time_frame": time_frame.time_frame.id,
                    "name": time_frame.name_2.id,
                    "amount": total,
        })
        return res

    @api.onchange('amount_2')
    def _amount_2(self):
        self.amount_3 = self.amount_2 - self.amount

    @api.onchange('pull')
    def _pull(self):
        payment = []
        if self.pull:
            time_frame = self.env['membership.payment'].search([('time_frame', '=', self.time_frame.id)])
            for line in time_frame:
                payment.append(line.id)
            print(payment)
            self.payments = [(6, 0, payment)]


    def register(self):
        inv_values = {
            'name_2': self.name.id,
            'amount': self.amount,
            'amount_2': self.amount_2,
            'amount_3': self.amount_3,
            'fiscal_year': self.fiscal_year.id,
            'time_frame': self.time_frame.id,
            'payments': [(6,0,self.payments.ids)],
            'woreda': self.woreda.id,

        }
        print("inv_values", inv_values)
        move = self.env['sub.payment'].sudo().create(inv_values)
        # for serv in self.service:
        #     serv.state = 'register'
        #     serv.account_move_id = move.id
        return