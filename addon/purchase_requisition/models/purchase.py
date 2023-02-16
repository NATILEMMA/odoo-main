# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

class PurchaseOrderLineUnlink(models.Model):
    _name = 'purchase.order.line.unlink'

    name = fields.Text(string='Description', required=True)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True)
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')

    price_subtotal = fields.Float(string='Subtotal', store=True)
    price_total = fields.Float(string='Total', store=True)
    price_tax = fields.Float(string='Tax', store=True)
    par_id = fields.Many2one('purchase.requisition', string='Partner')
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True,
                                 store=True)
    requisition_id_2 = fields.Many2one('purchase.requisition', string='Partner')
    order_line = fields.Many2one('purchase.order', string='line')
    selection = fields.Selection([
        ("selected", "selected"),
        ("failed", "failed"),
         ], default='failed')
    reason = fields.Char('Reason')

    @api.onchange('selection')
    def _onchange_requisition_id(self):
        print("ord", self.order_line)
        for line in self.order_line.order_line:
            print("line.product_id.id == self.product_id.id", line.product_id.id , self.product_id.id)
            if line.product_id.id == self.product_id.id:
                if self.selection == "selected":
                  print("line.selection", line.selection)
                  line.selection = "selected"
                  print("line.selection", line.selection)
                elif self.selection == "failed":
                    line.selection = "failed"


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    requisition_id = fields.Many2one('purchase.requisition', string='Purchase Agreement', copy=False)
    is_quantity_copy = fields.Selection(related='requisition_id.is_quantity_copy', readonly=False)

    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
        request = self.env['purchase.requisition'].search([('id', '=', self.requisition_id.id)])
        self.request_id = request.request_line_id.id
        if not self.requisition_id:
            active = self.env.context.get('active_ids', [])
            print("active", active[0])
            self.request_id = active[0]
            return

        requisition = self.requisition_id
        if self.partner_id:
            partner = self.partner_id
        else:
            partner = requisition.vendor_id
        payment_term = partner.property_supplier_payment_term_id

        FiscalPosition = self.env['account.fiscal.position']
        fpos = FiscalPosition.with_context(force_company=self.company_id.id).get_fiscal_position(partner.id)
        fpos = FiscalPosition.browse(fpos)

        self.partner_id = partner.id
        self.fiscal_position_id = fpos.id
        self.payment_term_id = payment_term.id,
        self.company_id = requisition.company_id.id
        self.currency_id = requisition.currency_id.id
        if not self.origin or requisition.name not in self.origin.split(', '):
            if self.origin:
                if requisition.name:
                    self.origin = self.origin + ', ' + requisition.name
            else:
                self.origin = requisition.name
        self.notes = requisition.description
        self.date_order = fields.Datetime.now()

        if requisition.type_id.line_copy != 'copy':
            return

        # Create PO lines if necessary
        order_lines = []
        for line in requisition.line_ids:
            # Compute name
            product_lang = line.product_id.with_context(
                lang=partner.lang,
                partner_id=partner.id
            )
            name = product_lang.display_name
            if product_lang.description_purchase:
                name += '\n' + product_lang.description_purchase

            # Compute taxes
            if fpos:
                taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id)).ids
            else:
                taxes_ids = line.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == requisition.company_id).ids

            # Compute quantity and price_unit
            if line.product_uom_id != line.product_id.uom_po_id:
                product_qty = line.product_uom_id._compute_quantity(line.product_qty, line.product_id.uom_po_id)
                price_unit = line.product_uom_id._compute_price(line.price_unit, line.product_id.uom_po_id)
            else:
                product_qty = line.product_qty
                price_unit = line.price_unit

            if requisition.type_id.quantity_copy != 'copy':
                product_qty = 0

            # Create PO line
            order_line_values = line._prepare_purchase_order_line(
                name=name, product_qty=product_qty, price_unit=price_unit,
                taxes_ids=taxes_ids)
            order_lines.append((0, 0, order_line_values))
        self.order_line = order_lines

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for po in self:
            if not po.requisition_id:
                continue
            if po.requisition_id.type_id.exclusive == 'exclusive':
                others_po = po.requisition_id.mapped('purchase_ids').filtered(lambda r: r.id != po.id)
                others_po.button_cancel()
                if po.state not in ['draft', 'sent', 'to approve']:
                    po.requisition_id.action_done()
        return res

    @api.model
    def create(self, vals):
        purchase = super(PurchaseOrder, self).create(vals)
        if purchase.requisition_id:
            purchase.message_post_with_view('mail.message_origin_link',
                    values={'self': purchase, 'origin': purchase.requisition_id},
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'))
        return purchase

    def write(self, vals):
        result = super(PurchaseOrder, self).write(vals)
        if vals.get('requisition_id'):
            self.message_post_with_view('mail.message_origin_link',
                    values={'self': self, 'origin': self.requisition_id, 'edit': True},
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'))
        return result


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    selection = fields.Selection([
        ("selected", "selected"),
        ("failed", "failed"),
        ("uncompered", "not compered")
         ], default='uncompered')
    reason = fields.Char('Reason')

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        res = super(PurchaseOrderLine, self)._onchange_quantity()
        if self.order_id.requisition_id:
            for line in self.order_id.requisition_id.line_ids.filtered(lambda l: l.product_id == self.product_id):
                if line.product_uom_id != self.product_uom:
                    self.price_unit = line.product_uom_id._compute_price(
                        line.price_unit, self.product_uom)
                else:
                    self.price_unit = line.price_unit
                break
        return res

    def create(self, vals):

            account_ids = self.env.context.get('active_ids', [])
            acc = self.env['purchase.requisition'].browse(account_ids[0])
            pur = self.env['purchase.order'].browse(vals.get('order_id'))
            print("line", vals.get('order_id'), acc.id, pur.requisition_id.id)
            # if line.order_id.state in ['purchase', 'done']:
            #     raise UserError(_('Cannot delete a purchase order line which is in state \'%s\'.') % (line.state,))
            # print('line.tender.id == account_ids[0]', line.tender.id, account_ids[0])
            terms = []
            if pur.requisition_id.id == account_ids[0]:
                values = {}
                values['product_id'] = vals.get('product_id')
                values['product_qty'] = vals.get('product_qty')
                values['price_unit'] = vals.get('price_unit')
                values['name'] = vals.get('name')
                values['partner_id'] = pur.partner_id.id
                values['price_subtotal'] = vals.get('price_subtotal')
                values['price_total'] = vals.get('price_total')
                values['taxes_id'] =  vals.get('taxes_id')
                values['order_line'] = pur.id

                terms.append((0, 0, values))
                acc.line_id_2 = terms
                print("terms", terms)
            return super(PurchaseOrderLine, self).create(vals)
