# -*- coding: utf-8 -*-
# Copyright 2015 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class AccountVoucherWizard(models.TransientModel):

    _name = "account.purchase.voucher.wizard"
    journal_id = fields.Many2one('account.journal', 'Journal', default=lambda self:
                                    self.env['account.journal'].search([('name', '=', 'Vendor Bills')]),
                                 required=True, readonly=True)
    amount_total = fields.Float('Amount total', readonly=True)
    amount_advance = fields.Float('Amount advanced', required=True,
                                  digits_compute=
                                  dp.get_precision('Sale Price'))
    date = fields.Date("Date", required=True,
                       default=fields.Date.context_today)
    exchange_rate = fields.Float("Exchange rate", digits=(16, 6), default=1.0,
                                 readonly=True)
    currency_id = fields.Many2one("res.currency", "Currency", readonly=True)
    currency_amount = fields.Float("Curr. amount", digits=(16, 2),
                                   readonly=True)
    payment_ref = fields.Char(string="Reference")
    credit_account_id = fields.Many2one("account.account",
                                        string="Credit Account", domain=[('user_type_id', '=', 'Receivable')],
                                        help="Account used for bank deposit")
    purchase_account = fields.Many2one("account.account", string="debit Account")
    payment_Type = fields.Selection([
        ('Direct', 'Direct payment'),
        ('employee', 'Payment by employee')],
        string='Payment type', required=True, default='employee')

    @api.constrains('amount_advance')
    def check_amount(self):
        if self.amount_advance <= 0:
            raise exceptions.ValidationError(_("Amount of advance must be "
                                               "positive."))
        if self.env.context.get('active_id', False):
            order = self.env["purchase.order"].\
                browse(self.env.context['active_id'])
            if self.amount_advance > order.amount_resisual:
                raise exceptions.ValidationError(_("Amount of advance is "
                                                   "greater than residual "
                                                   "amount on purchase"))

    @api.model
    def default_get(self, fields):
        res = super(AccountVoucherWizard, self).default_get(fields)
        purchase_ids = self.env.context.get('active_ids', [])
        if not purchase_ids:
            return res
        purchase_id = purchase_ids[0]

        purchase = self.env['purchase.order'].browse(purchase_id)

        amount_total = purchase.amount_resisual
        if purchase.payment_agreement == 'full':
            amount_total_2 = purchase.amount_resisual
        else:
            amount_total_2 = purchase.adv
        if 'amount_total' in fields:
            res.update({'amount_total': amount_total,
                        'currency_id': purchase.currency_id.id,
                         'amount_advance': amount_total_2,
                        })

        return res


    @api.onchange('amount_advance')
    def onchange_amount(self):
        self.currency_amount = self.amount_advance * (1.0 / self.exchange_rate)

    
    def make_advance_payment(self):
        """Create customer paylines and validates the payment"""
        print("make_advance_payment")
        approval_limt_ary = self.env['purchase.approval.limit'].search([])
        print(approval_limt_ary)
        flag = False
        for approval_limt in approval_limt_ary:
            print(approval_limt, approval_limt.user_id.id, self.env.user.id)
            approver_user_id = approval_limt.user_id.id
            if approver_user_id == self.env.user.id:
                print(approver_user_id, self.env.user.id, approval_limt.max_amount_2, self.amount_total)
                if approval_limt.max_amount_2 >= self.amount_total:
                    flag = True
                else:
                    raise ValidationError(
                        _("The advance amount is larger than your approval limit"))
        if not flag:
             raise ValidationError(
                        _("you do not approval limit"))
        no_post = self._context.get('no_post', False)
        payment_obj = self.env['account.payment']
        purchase_ids = self.env.context.get('active_ids', [])
        if purchase_ids:
            payment_res = self.get_payment_res(purchase_ids)
            payment = payment_obj.create(payment_res)
            # if not no_post:
            #     payment.post()
        return {
            'type': 'ir.actions.act_window_close',
        }


    def get_payment_res(self, purchase_ids):
        purchase_obj = self.env['purchase.order']

        purchase_id = purchase_ids[0]
        purchase = purchase_obj.browse(purchase_id)

        # partner_id = purchase.partner_id.id
        partner_id = self.env['res.users'].search([('id', '=', self.env.uid)]).partner_id
        
        partner_id = purchase.user_id.partner_id.id
        type = self[0].payment_Type
        date = self[0].date
        company_id = purchase.company_id

        payment_res = {'payment_type': 'outbound',
                       'partner_id': partner_id,
                       'partner_type': 'supplier',
                       'journal_id': self[0].journal_id.id,
                       'company_id': company_id.id,
                       'currency_id': purchase.currency_id.id,
                       'payment_date': date,
                       'amount': self[0].amount_advance,
                       'purchase_id': purchase.id,
                       'name': _("Advance Payment") + " - " + purchase.name,
                       'communication': self[0].payment_ref or purchase.name,
                       'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
                       'payment_Type': type,

                       }
        return payment_res