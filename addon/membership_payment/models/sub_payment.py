from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class Payment(models.Model):
    _inherit = "membership.payment"
    _description = "This model will handle with the payment of memberships"

    sub_city = fields.Many2one('sub.payment', string="Fiscal year")


class SubPayment(models.Model):
    _name = "sub.payment"
    _description = "This model will help to handel subcity payment"


    name = fields.Char(string="Subcity", defualt='draft', readonly= True)
    name_2 = fields.Many2one('membership.handlers.parent', string="Subcity", required=True)
    amount = fields.Float(string='amount')
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True, )
    city = fields.Many2one('city.payment', string="Fiscal year")
    time_frame = fields.Many2one('reconciliation.time.fream', string='Time frame',
                                 domain="[('fiscal_year', '=', fiscal_year)]", required=True, )
    payments = fields.One2many('membership.payment','sub_city', string='payments')
    woreda = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', name_2)]", required=True)
    user = fields.Many2one('res.users')
    woreda = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', name_2)]", required=True)
    supporter = fields.One2many('supporter.payment', 'rev', string='supporter payment')
    amount_2 = fields.Float(string='Amount received')
    amount_3 = fields.Float(string='Diffrence')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('register','Register'),], default='draft', string="Status")


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('Woreda.payment')
        vals.update({'name': seq})

        return super(SubPayment, self).create(vals)

    @api.onchange('time_frame', 'woreda')
    def _get_lines_2(self):
          if self.time_frame and self.woreda:
            member = self.env['membership.payment'].search([('month', '=', self.time_frame.id),('wereda_id', '=', self.woreda.id)])
            val = []
            val_2 = []
            amount = 0
            for line in member:
              if line.state == 'submit':
                amount = line.amount + amount
                if not line.payment_for_supporter:
                 val.append(line.id)
                else:
                    val_2.append((0, 0, {
                        'sup': line.supporter_ids.id,
                        'amount': line.amount,
                    }))

            self.user = self.woreda.branch_manager.id
            self.payments = val
            self.supporter = val_2
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
            line.state = 'draft'
        self.state = 'draft'

    def set_submit(self):
        for line in self.payments:
            line.state = 'registered'
        self.state = 'submit'


class SupporterPayment(models.Model):
    _name = 'supporter.payment'

    rev = fields.Many2one("sub.payment")
    sup = fields.Many2one("supporter.members", string='members')
    amount = fields.Float("amount")