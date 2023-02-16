from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
import json
from odoo.exceptions import UserError, ValidationError


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('biding.product', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                      string="Attachment", invisible=1)
    attach_rel = fields.Many2many('vendor.partner', 'attach_id', 'attachment_id3', 'document_id',
                                  string="Attachment", invisible=1)

class BidingProduct(models.Model):
    _name = 'biding.product'
    _description = 'biding product'
#
    name = fields.Char(string='Rule name')
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)
    is_pass = fields.Boolean('passed')
    input_type = fields.Selection(
        [('attach', 'Attach file'),
         ('selection', 'selection'),
         ('tick', 'Yes/No'),
         ('price', 'price'),
         ], string="Input Type")
    amount = fields.Float(string="Amount")
    rule = fields.Many2one('product.document', string='rule')
    selection = fields.Many2one('product.selected', domain="[('product_id', '=', rule)]", string='selection')
    purchase = fields.Many2one('purchase.order', string='vendor')
    value = fields.Float(string="value in %", required=True, digits=(12, 2))


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = 'Purchase Order'

    rule = fields.One2many('biding.product', 'purchase', string='rule')
    agreement = fields.Many2one('purchase.requisition', related='requisition_id', string='Purchase agreement')
    state_of_requisition = fields.Selection(related='requisition_id.state')
    status =  fields.Selection([('failed', 'Failed'), ('passed', 'Passed')])

    def button_confirm(self):
        """This function will make change the status of the not selected vendors to Cancel"""
        orders = self.env['purchase.order'].search([('requisition_id', '=', self.requisition_id.id)])
        print(orders)
        print(self)
        for order in orders:
            if order != self:
                order.write({'state': 'cancel'})
        return super(PurchaseOrder, self).button_confirm()


    @api.onchange('partner_id')
    def _make_agreement_change(self):
        """This function will determine the value of agreement in partner"""
        for record in self:
            active_id = self.env.context.get('active_id')
            record.partner_id.agreement = active_id
            if not record.partner_id.rule:
                rules = self.env['vendor.document'].search([('agreement', '=', record.partner_id.agreement.id)])
                terms = []
                for rule in rules:
                    values = {}
                    values['name'] = rule.name
                    values['input_type'] = rule.input_type
                    values['rule'] = rule.id
                    values['value'] = rule.value

                    terms.append((0, 0, values))
                record.partner_id.rule = terms

    @api.onchange('agreement')
    def onchange_input_type(self):
        if self.rule:
            self.rule = [(6, 0, 0)]
        rules = self.env['product.document'].search([('agreement', '=', self.agreement.id)])
        terms = []
        for rule in rules:
            values = {}
            values['name'] = rule.name
            values['input_type'] = rule.input_type
            values['rule'] = rule.id
            values['value'] = rule.value

            terms.append((0, 0, values))
        self.rule = terms


class PurchaseOrderLineInherit(models.Model):
    _inherit = "purchase.order.line"

    status =  fields.Selection([('failed', 'Failed'), ('passed', 'Passed')])

