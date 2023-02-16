# -*- coding: utf-8 -*-
# Copyright 2015 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    flag = fields.Float(string="Is Change", compute="_get_amount_flag")
    payment_agreement = fields.Selection([
        ('full', 'Full Payment'),
        ('advance', 'Advance Payment')],
        string='Payment Agreement', required=True, default='full')
    adv = fields.Float(string="Advance Amount")
    is_merge = fields.Boolean(string="Is merged order", default=False)

    def _get_amount_flag(self):
        advance_amount = 0.0
        self.flag = 0.0
        print("_get_amount_flag")
        for line in self.account_payment_ids:
            if line.state != 'draft':
                advance_amount += line.amount
            else:
                self.flag += line.amount



    def _get_amount_residual(self):
        print('_get_amount_residual')
        advance_amount = 0.0

        for line in self.account_payment_ids:
                advance_amount += line.amount
        self.amount_resisual = self.amount_total - advance_amount

    account_payment_ids = fields.One2many('account.payment', 'purchase_id',
                                          string="Pay purchase advanced")
    amount_resisual = fields.Float('Residual amount', readonly=True,
                                   compute="_get_amount_residual")

    def button_cancel(self):
        for line in self.account_payment_ids:
            line.unlink()

        return super(PurchaseOrder, self).button_cancel()
