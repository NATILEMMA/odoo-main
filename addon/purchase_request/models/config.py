from odoo import api, fields, models, _ , SUPERUSER_ID

class PurchaseApprovalLimit(models.Model):
    _name = 'purchase.approval.limit'
    _description = 'Purchase Aproval Limit'    
    _inherit = ['mail.thread', 'mail.activity.mixin']
#    _rec_name="user_id"

    product = fields.Many2one('product.product')                               
    product_catagory = fields.Many2one('product.category')                               
    user_id = fields.Many2one('res.users')
    max_amount = fields.Float()
    max_amount_2 = fields.Float()
    limit_by = fields.Selection(string='Limit By', default='product',
                                     selection=[('product','Product'),
                                         ('product_catagory','Product Catagory')])

    # @api.model
    # def create(self, vals):

    #     active_id = self._context('active_ids')
    #     spro_purchase_request = self.env['sprogroup.purchase.request'].search([('id', '=', active_id)],limit=1)
    #     spro_purchase_request.write({'state': 'leader_approved'})
    #     return  super(PurchaseApprovalLimit, self).create(vals)

        
        


