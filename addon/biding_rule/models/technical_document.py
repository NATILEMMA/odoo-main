from datetime import datetime, date, timedelta
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
import json
from odoo.exceptions import UserError, ValidationError

class ProductSelected(models.Model):
    _name="product.selected"
    _description="This models will create selected option to product"


    name = fields.Char()
    value = fields.Float()
    product_id = fields.Many2one('product.document')

class SelectionField(models.Model):
    _name = 'selection.field_2'
    _description = 'selection field'

    name = fields.Char(string='selection name', required=True)
    value = fields.Float(string="selection value", digits=(12, 2))
    vendor_document_id = fields.Many2one('product.document', string='Product document', readonly=True)
    

class ProductDocument(models.Model):
    _name = 'product.document'
    _description = 'product Documents'

    name = fields.Char(string='Rule name', required=True, copy=False, help='You can give your'
                                                                                 'Document number.')
    description = fields.Text(string='Description', copy=False, help="Description")
    issue_date = fields.Date(string='Issue Date', default=fields.datetime.now(), help="Date of issue", copy=False)
    is_pass = fields.Boolean('passed')
    input_type = fields.Selection(
        [('attach', 'Attach file'),
         ('selection', 'selection'),
         ('tick', 'Yes/No'),
         ('price', 'price')
         ], string="Input Type")

    selection = fields.Many2many('selection.field_2', domain="[('vendor_document_id', '=', 0)]", string='selection')
    agreement = fields.Many2one('purchase.requisition', string='agreement')
    selection_view = fields.Boolean('To see selection')
    number = fields.One2many('number.document_2', 'doc',string='numbering')
    value = fields.Float(string="value in %", digits=(12, 2))

    @api.onchange('selection')
    def get_prices(self):
        for line in self.selection:
            line.vendor_document = self.id

    @api.model
    def create(self, vals):
        all_selected = vals['selection']
        agreement_id = self.env.context.get('active_ids', [])
        vals.update({'agreement': agreement_id[0],
                      'selection_view': True,
                     })
        res = super(ProductDocument, self).create(vals)
        for i in all_selected[0][2]:
            value = self.env['selection.field_2'].search([('id', '=', i)])
            self.env['product.selected'].sudo().create({
                                                      'name': value['name'],
                                                      'value': value['value'],
                                                      'product_id': res.id
                                                      })
        return res

class NumberSelection(models.Model):
    _name = 'number.document_2'
    _description = 'numeber Documents'

    amount = fields.Float(string="Amount")
    value = fields.Float(string="value in %", digits=(12, 2))
    doc = fields.Many2one('vendor.document', string='doc')
