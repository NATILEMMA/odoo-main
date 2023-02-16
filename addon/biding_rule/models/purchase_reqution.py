from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
import json
from odoo.exceptions import UserError, ValidationError


class RequisitionResult(models.Model):
    _name = "requisition.result"
    _description = 'requisition result'

    order_id = fields.Many2one('purchase.order', string='Purchase order')
    vendor_id = fields.Many2one('res.partner', related="order_id.partner_id")
    req = fields.Many2one('purchase.requisition', string='Purchase order')
    amount = fields.Float(string="Product result", digits=(12, 2))
    amount_2 = fields.Float(string="Professional result", digits=(12, 2))
    amount_4 = fields.Float(string="Total result", digits=(12, 2))
    amount_3 = fields.Float(string="Adjustment", digits=(12, 2))
    selection = fields.Selection(
        [('pass', 'pass'),
         ('fail', 'fail')
         ], defulet='fail', string="Status")
    reason = fields.Char(string='Reason')
    product_results = fields.Char()
    professional_results = fields.Char()


class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"
    _description = 'purchase requisition Documents'

    document_count = fields.Integer(compute='_document_count', string='# Documents')
    document_count_2 = fields.Integer(compute='_document_count_2', string='# Documents')
    res_one = fields.One2many('requisition.result', 'req', string='Result')
    vendor_document_value_count = fields.Float(compute='_document_count')
    product_document_value_count = fields.Float(compute='_document_count_2')
    hundred_percent = fields.Float(compute="_total_values")


    def action_open(self):
        """Before bid is validated this function will check if all tendors submitted atleast price"""
        for record in self.purchase_ids:
            for line in record.order_line:
                if line.price_unit != 0.00:
                    line.write({'status': 'passed'})
                    self.env.cr.commit()
                else:
                    line.write({'status': 'failed'})
                    self.env.cr.commit()
        for record in self.purchase_ids:
            if 'failed' not in record.order_line.mapped('status'):
                record.write({'status': 'passed'})
                self.env.cr.commit()
            else:
                record.write({'status': 'failed'})
                self.env.cr.commit()
                raise UserError(_("Bid Can Not Be Selected Until All Bidders Submit Atleast Their Price Offer. Please Go Back And Check On Products That Are Red."))
        return super(PurchaseRequisition, self).action_open()

    def _document_count(self):
        for each in self:
            document_ids = self.env['vendor.document'].sudo().search([('agreement', '=', self.id)])
            each.document_count = len(document_ids)
            values = document_ids.mapped('value')
            total = 0
            for value in values:
                total += value
            each.vendor_document_value_count = total

    def _document_count_2(self):
        for each in self:
            document_id = self.env['product.document'].sudo().search([('agreement', '=', self.id)])
            each.document_count_2 = len(document_id)
            values = document_id.mapped('value')
            total = 0
            for value in values:
                total += value
            each.product_document_value_count = total 

    def action_in_progress(self):
        """This function will modify the confirm button according to the values in rules"""
        for record in self:
            record.hundred_percent = record.vendor_document_value_count + record.product_document_value_count
            if record.hundred_percent < 100.00:
                raise UserError(_("Sum of the values of Product and Professional must be exactly 100%"))
            elif record.hundred_percent > 100.00:
                raise UserError(_("Sum of the values of Product and Professional must be exactly 100%"))
            return super(PurchaseRequisition, self).action_in_progress()

    def document_view(self):
        self.ensure_one()
        return {
            'name': _('Professional Rule'),
            'domain': [('agreement', '=', self.id)],
            'res_model': 'vendor.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Rule
                        </p>'''),
            'limit': 80,
        }

    def document_view_2(self):
        self.ensure_one()
        return {
            'name': _('Product Rule'),
            'domain': [('agreement', '=', self.id)],
            'res_model': 'product.document',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Rule
                        </p>'''),
            'limit': 80,
        }

    def result(self):
        terms = []
        if self.res_one:
            self.res_one = [(6,0,0)]
        amount_totals = self.purchase_ids.mapped('amount_total')
        order_amount_total = sorted(amount_totals)
        the_lowest_price_id = self.purchase_ids.filtered(lambda rec: rec.amount_total == order_amount_total[0]).id
#        for prc in self.purchase_ids:
#            price_flag = price_flag + 1
#            if price_flag == 1:
#                price = prc.amount_total
#            else:
#                if price > prc.amount_total:
#                    price = prc.amount_total

        for purchase in self.purchase_ids:
            products = 0
            prof_products = 0
            professional_names = ''
            product_names = ''
            for rule in purchase.rule:
                value = (rule.value) / 100
                if rule.input_type == 'attach':
                    if rule.doc_attachment_id:
                        products += value
                        name = rule.name + ' = ' + str(value * 100) + '\n'
                        product_names += name
                elif rule.input_type == 'selection':
                    val = (rule.selection.value / 100) * value
                    products += val
                    name = rule.name + ' = ' + str(val * 100) + '\n'
                    product_names += name
                elif rule.input_type == 'price':
                    if purchase.id == the_lowest_price_id:
                        products += value
                        name = rule.name + ' = ' + str(value * 100) + '\n'
                        product_names += name
                elif rule.input_type == 'tick':
                    if rule.is_pass:
                        products += value
                        name = rule.name + ' = ' + str(value * 100) + '\n'
                        product_names += name
            for line in purchase.partner_id.rule:
                value = (line.value) / 100
                if line.input_type == 'attach':
                    if line.attach_id:
                        prof_products += value
                        name = line.name + ' = ' + str(value * 100) + '\n'
                        professional_names += name
                elif line.input_type == 'selection':
                    val = (line.selection.value / 100) * value
                    prof_products += val
                    name = line.name + ' = ' + str(val * 100) + '\n'
                    professional_names += name
                elif line.input_type == 'employee':
                    val = (purchase.partner_id.value_2 / 100) * value
                    prof_products += val
                    name = line.name + ' = ' + str(val * 100) + '\n'
                    professional_names += name
                elif line.input_type == 'financial':
                    val = (purchase.partner_id.value / 100) * value
                    prof_products += val
                    name = line.name + ' = ' + str(val * 100) + '\n'
                    professional_names += name
                elif line.input_type == 'tick':
                   if line.is_pass:
                     prof_products += value
                     name = line.name + ' = ' + str(value * 100) + '\n'
                     professional_names += name
            terms.append((0, 0, {
                            'order_id': purchase.id,
                            'amount_2': prof_products * 100,
                            'amount': products * 100,
                            'amount_4': (products + prof_products) * 100,
                            'amount_3': (products + prof_products) * 100,
                            'professional_results': professional_names,
                            'product_results': product_names,
                        }))
        self.res_one = terms
        totals = self.res_one.mapped('amount_4')
        highest_result = sorted(totals)
        highest_amount = highest_result[-1]
        highest_bidder = self.res_one.filtered(lambda res: res.amount_4 == highest_amount)
        highest_bidder.selection = 'pass'
        for results in self.res_one:
            if results.selection != 'pass':
                results.selection = 'fail'
#        flag = 0
#        for res in self.res_one:
#            flag = flag + 1
#            if flag == 1:
#              amount = res.amount_4
#            else:
#                if amount < res.amount_4:
#                    amount = res.amount_4
#        print("amount", amount)
#        for res_2 in self.res_one:
#            if res_2.amount_4 == amount:
#                res_2.selection = 'pass'
#            else:
#                res_2.selection = 'fail'

    def action_done(self):
        for res_2 in self.res_one:
            if res_2.selection == 'fail':
                res_2.order_id.state = 'cancel'

        return super(PurchaseRequisition, self).action_done()
