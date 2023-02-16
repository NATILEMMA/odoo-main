from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class CityPayment(models.Model):
    _name = "city.payment"
    _description = "This model will help to handel subcity payment"


    name = fields.Char(string="Subcity", defualt='draft', readonly= True)
    name_2 = fields.Many2one('membership.handlers.parent', string="Subcity", required=True)
    amount = fields.Float(string='amount')
    main = fields.Many2one('main.branch', string="Fiscal year")
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True, )
    time_frame = fields.Many2one('reconciliation.time.fream', string='Time frame',
                                 domain="[('fiscal_year', '=', fiscal_year)]", required=True, )
    payments = fields.One2many('sub.payment', 'city', string='payments')
    amount_2 = fields.Float(string='Amount received')
    amount_3 = fields.Float(string='Diffrence')
    amount_2 = fields.Float(string='Amount received')
    amount_3 = fields.Float(string='Diffrence')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('register', 'Register'), ], default='draft', string="Status")
    user = fields.Many2one('res.users')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('sub.city.payment')
        vals.update({'name': seq})

        return super(CityPayment, self).create(vals)

    @api.onchange('time_frame', 'name_2')
    def _get_lines_2(self):
        if self.time_frame and self.name_2:
            member = self.env['sub.payment'].search(
                [('time_frame', '=', self.time_frame.id), ('name_2', '=', self.name_2.id)])
            val = []
            amount = 0
            for line in member:
               if line.state == 'submit':
                    amount = line.amount + amount
                    val.append(line.id)
            self.user = self.name_2.parent_manager.id
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

    def set_submit(self):
        for line in self.payments:
            line.state = 'register'
        self.state = 'submit'
