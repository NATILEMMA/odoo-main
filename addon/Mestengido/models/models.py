import logging
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tokenize import group
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
import os
from odoo.exceptions import UserError, Warning, ValidationError
import re
import base64
import requests
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)

MONTH = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), 
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ]
QUARTER = [
        ('1st', 'First Quartner'),
        ('2nd', 'Second Quarter'),
        ('3rd','Third Quarter'),
        ('4th', 'Fourth Quarter')
]
STATES = [
    ('draft', 'requested'),
    ('submitted', 'To be approve'),
    ('approved','Approved'),
    ('canceled', 'Cancel'),
    ('done', 'Done'),
]

STATES_ORDER = [
    ('request', 'REQ'),
    ('ready', 'Ready'),
    ('posted', 'posted to Purchase order'),
    ('canceled', 'Cancel')
]



class Mestengido(models.Model):
    _name = 'mest.mest'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    @api.model
    def year_selection(self):
        year = 2000 # replace 2000 with your a start year
        year_list = []
        while year != 2030: # replace 2030 with your end year
            year_list.append((str(year), str(year)))
            year += 1
        return year_list


    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done

    @api.model
    def _get_default_partner(self):
        if 'default_mest_id' in self.env.context:
            default_mest_id = self.env['mest.mest'].browse(self.env.context['default_mest_id'])
            return default_mest_id.exists().partner_id


    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.order_line:
                line.sequence = current_sequence
                current_sequence += 1

    def write(self, line_values):
        res = super(Mestengido, self).write(line_values)
        self._reset_sequence()
        return res

    def copy(self, default=None):
        return super(Mestengido,
                     self.with_context(keep_line_sequence=True)).copy(default)

    @api.depends('order_line')
    def _compute_max_line_sequence(self):
        _logger.info("orderrrrrrrrrrrrrrrrrrrrrline")
        for sale in self:
            sale.max_line_sequence = (
                max(sale.mapped('order_line.sequence') or [0]) + 1)


    department_id = fields.Many2one('hr.department','Department')
    name = fields.Char('Name')
    description = fields.Html('Internal Note')
    month = fields.Selection(MONTH,
                          string='Month',default="1", store=True,)
    year = fields.Selection(
        year_selection,
        string="Year",
        default="2015", # as a default value it would be 2019)
    )
    quarter = fields.Selection(QUARTER,
                          string='Quarter', store=True,)
    state = fields.Selection(STATES,
                              'Status', required=True,
                              copy=False, default='draft',tracking=True)
    max_line_sequence = fields.Integer(
        string='Max sequence in lines',
        compute='_compute_max_line_sequence',
        store=True
    )
    order_line = fields.One2many('mest.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    partner_id = fields.Many2one('res.partner',
        string='Customer',
        default=lambda self: self._get_default_partner(),
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    requester_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user, tracking=True)
    create_date = fields.Date()

    requster_signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    requster_signed_by = fields.Char('Signed By', help='Name of the person that signed the SO.', copy=False)
    requster_signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)

    approver_signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    approver_signed_by = fields.Char('Signed By', help='Name of the person that signed the SO.', copy=False)
    approver_signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)
    approver_comment = fields.Char()
    
    final_approver_signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    final_approver_signed_by = fields.Char('Signed By', help='Name of the person that signed the SO.', copy=False)
    final_approver_signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)
    final_approver_comment = fields.Char()

    
    squ = fields.Char(string='reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
    max_line_sequence = fields.Integer(
        string='Max sequence in lines',
        compute='_compute_max_line_sequence',
        store=True
    )

    
    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.order_line:
                line.sequence = current_sequence
                current_sequence += 1

    def write(self, line_values):
        res = super(Mestengido, self).write(line_values)
        self._reset_sequence()
        return res

    def copy(self, default=None):
        return super(Mestengido,
                     self.with_context(keep_line_sequence=True)).copy(default)

  
    
    @api.model
    def create(self, vals):
        
        _logger.info("Vals :%s",vals)
        _logger.info(self.department_id)
        months = [('1', 'January'),('2', 'February'),('3', 'March'),('4', 'April'),('5', 'May'),('6', 'June'),('7', 'July'),('8', 'August'), ('9', 'September'),('10', 'October'), ('11', 'November'), ('12', 'December')]
        month_name = dict(months).get(vals.get('month'))
        department = self.env['hr.department'].search([('id','=',vals['department_id'])],limit=1)
        _logger.info("########## %s",department)
        _logger.info("########## %s",vals['department_id'])

        vals['name'] = '%s - %s - %s - Requests' % (department.name,month_name, vals.get('year'))
        vals['squ'] = self.env['ir.sequence'].next_by_code('mest.mest') or _('New')
        return super(Mestengido, self).create(vals)
        


 

    def action_request(self):
        self.state = "submitted"
        
        super(Mestengido, self).write({'state':'submitted','create_date': datetime.now()})

    def action_submit(self):
        self.state = "approved"
        self.user_id = self.env.uid
        super(Mestengido, self).write({'state':'approved','user_id': self.env.uid})

  
   
    def action_cancel(self):
        self.state = "canceled"
        super(Mestengido, self).write({'state':'canceled'})
        
    

class MestengidoOrderLine(models.Model):
    _name = 'mest.order.line'
    _description = 'Mestengido Order Line'
    _order = 'order_id, sequence, id'


    name = fields.Text(string='Description')
    product_qty = fields.Integer(string='Quantity', digits='Product Unit of Measure')
    product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True)
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True)
    product_type = fields.Selection(related='product_id.type', readonly=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    order_id = fields.Many2one('mest.mest', string='Request Reference', index=True, required=True, ondelete='cascade')
    sequence = fields.Integer(
        help="Gives the sequence of this line when displaying.",
        default=1,
        string="S.No"
    )

   
    sequence2 = fields.Integer(
        help="Shows the sequence of this line.",
        related='sequence',
        string="No",
        readonly=True,
        store=True
    )

    @api.model
    def create(self, values):
        line = super(MestengidoOrderLine, self).create(values)
        if self.env.context.get('keep_line_sequence'):
            line.order_id._reset_sequence()
        return line
    
    @api.depends('order_line')
    def _chech_value(self):
        _logger.info("#######################")
        _logger.info(self.sequence2)
        _logger.info(self.product_id.name)
        _logger.info(len(self.product_id))
        sale_order = self.env['sale.order'].sudo().search([('state','like','draft')])
        _logger.info(sale_order)
        if self.product_id != False:
            for l in range(len(sale_order)):
                for line in sale_order.order_line:
                    _logger.info("oooooooooooooounder")
                    _logger.info(line)
                    _logger.info(line.product_id)


   


class MestengidoOrderMonthlyTotal(models.Model):
    _name = 'monthly.amount'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    @api.model
    def year_selection(self):
        year = 2000 # replace 2000 with your a start year
        year_list = []
        while year != 2030: # replace 2030 with your end year
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    year = fields.Selection(
        year_selection,
        string="Year",
        default="2015", # as a default value it would be 2019)
    )

    amount = fields.Float("Amount")
    is_active = fields.Boolean(default="False")


class MestengidoOrder(models.Model):
    _name = 'mest.order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    @api.model
    def year_selection(self):
        year = 2000 # replace 2000 with your a start year
        year_list = []
        while year != 2030: # replace 2030 with your end year
            year_list.append((str(year), str(year)))
            year += 1
        return year_list


    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done

    @api.model
    def _get_default_partner(self):
        if 'default_mest_id' in self.env.context:
            default_mest_id = self.env['mest.mest'].browse(self.env.context['default_mest_id'])
            return default_mest_id.exists().partner_id


    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.order_line:
                line.sequence = current_sequence
                current_sequence += 1

    def write(self, line_values):
        res = super(MestengidoOrder, self).write(line_values)
        self._reset_sequence()
        return res

    def copy(self, default=None):
        return super(MestengidoOrder,
                     self.with_context(keep_line_sequence=True)).copy(default)

    @api.depends('order_line')
    def _compute_max_line_sequence(self):
        _logger.info("orderrrrrrrrrrrrrrrrrrrrrline")
        for sale in self:
            sale.max_line_sequence = (
                max(sale.mapped('order_line.sequence') or [0]) + 1)

    # @api.onchange('month')
    # def _getMonthlyrequest(self):
    #     month = self.month
    #     search = self.env['mest.mest'].search([('month','=',month)])
    #     _logger.info(search)
    #     for loop in search:
    #         self.requests = loop
    #     return search



    @api.depends('order_line.total_price')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            total_price =  0.0
            for line in order.order_line:
                total_price += line.total_price
                
            order.update({
                'total_price': total_price
            })

    requests = fields.Many2many('mest.mest')
    department_id = fields.Many2one('hr.department','Department')
    name = fields.Char('Name')
    description = fields.Html('Internal Note')
    month = fields.Selection(MONTH,
                          string='Month')
    year = fields.Selection(
        year_selection,
        string="Year",
        default="2015", # as a default value it would be 2019)
    )
    quarter = fields.Selection(QUARTER,
                          string='Quarter', store=True,)
    state = fields.Selection(STATES_ORDER,
                              'Status', required=True,
                              copy=False, default='request',tracking=True)
    max_line_sequence = fields.Integer(
        string='Max sequence in lines',
        compute='_compute_max_line_sequence',
        store=True
    )
    order_line = fields.One2many('mest.order.lines', 'order_id', string='Order Lines', default={})
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    partner_id = fields.Many2one('res.partner',
        string='Customer',
        default=lambda self: self._get_default_partner(),
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    requester_id = fields.Many2one('res.users', string='Requester', default=lambda self: self.env.user, tracking=True)
    create_date = fields.Date()
    analytic_account_id = fields.Many2one('account.analytic.account')
    total_price = fields.Float(string='Total Price', digits='Total Price', compute="_amount_all")
    requster_signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    requster_signed_by = fields.Char('Signed By', help='Name of the person that signed the SO.', copy=False)
    requster_signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)

    approver_signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    approver_signed_by = fields.Char('Signed By', help='Name of the person that signed the SO.', copy=False)
    approver_signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)
    approver_comment = fields.Char()
    
    final_approver_signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    final_approver_signed_by = fields.Char('Signed By', help='Name of the person that signed the SO.', copy=False)
    final_approver_signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)
    final_approver_comment = fields.Char()
    is_ture = fields.Boolean(default=False)


    
    squ = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
  

    @api.onchange('month')
    def _compute_monthly_request(self):
        # try:
        month = self.month
        search_request = self.env['mest.mest'].sudo().search([('month','=',month)])
        requests = []
        for request in search_request:
            self.year = request.year
            requests.append(request.id)
        self.requests = requests


        

                        
    @api.onchange('is_ture')
    def _compute_is_true(self):
        _logger.info("####### Is Ture #######")
        # try:
        requests = []
        order = []
        if self.is_ture == True:
            month = self.month
            
            search_request = self.env['mest.mest'].sudo().search([('month','=',month)])
            for request in self.requests:
                _logger.info("Request :%s",request.name)
                _logger.info("Orderline :%s",request.order_line)
                

                for line in request.order_line:
                    _logger.info("################ Line order %s",line)
                    data = {}
              
                    data['order_id'] = line.order_id.id
                    data['product_id'] = line.product_id.id
                    data['name'] = line.name
                    data['product_uom'] = line.product_uom.id
                    data['product_qty'] = line.product_qty
                    order.append((0,0,data))

                        
            _logger.info("Data %s",order)
            self['order_line'] = order
     
    def action_change_to_purchase_order(self):
        today = datetime.today()
        new_date = today + relativedelta(years=1)
        id = self.ids
        search_request = self.env['mest.mest'].sudo().search([('id','in',id)],limit=1)
        post_request = self.env['mest.order'].sudo().search([('id','in',self.ids)],limit=1)
        for loop in self.requests:
            loop.write({'state': 'approved'})
        amount_valid = self.env['monthly.amount'].search([('is_active','=', True)])
        _logger.info(amount_valid)
        _logger.info("%s-%s",amount_valid.amount,post_request.total_price)
        # try:
        if post_request.total_price <= amount_valid.amount:
            vals = {}
            data = {}
            data['date_approve'] = today
            data['partner_id'] = self.env.uid
            data['user_id'] = self.env.uid
            data['date_planned'] = today
            # data['state'] = 'dreft'
            create_PO = self.env['purchase.order'].sudo().create(data)

            for line in post_request.order_line:
                vals['order_id'] = create_PO.id
                vals['product_id'] = line.product_id.id
                vals['name'] = line.name
                vals['product_uom'] = line.product_uom.id
                vals['product_qty'] = line.product_qty
                vals['price_unit'] = line.price_unit
                vals['account_analytic_id'] = post_request.analytic_account_id.id

                POL = self.env['purchase.order.line'].sudo().create(vals)
        else:
            raise ValidationError("Your request is out of range. Your maximum allowable amount is " + str(amount_valid.amount) +" Birr")

        # except:
        #     raise UserWarning("Try later")
        super(MestengidoOrder, self).write({'state':'posted'})


    def action_merg(self):
        self.state = "ready"
        super(MestengidoOrder, self).write({'state':"ready"})


    # @api.model
    # def write(self, vals):
    #     _logger.info("###########  vals ###############:%s",vals)
    @api.model
    def create(self, vals):
       
        if "order_line" in vals.keys():
            _logger.info(vals.keys())
            product_list = []
            for obj in vals['order_line']:
                _logger.info(obj)
                if obj[2]['product_id'] not in product_list:
                    product_list.append(obj[2]['product_id'])
            list_new = vals['order_line']
            _logger.info(list_new)
            _logger.info("Product_list %s",product_list)
            new_list = []
            for obj in product_list:
                count = 0
                qty = 0
                price = 0
                for element in list_new:
                    _logger.info(obj)
                    _logger.info(element[2]['product_id'])
                    if obj == element[2]['product_id']:
                        qty += element[2]['product_qty']
                        _logger.info("quantity added %s",qty)
                        
                for ele in list_new:
                    if obj == ele[2]['product_id']:
                        count += 1
                        if count == 1:
                            ele[2]['product_qty'] = qty
                            ele[2]['product_qty'] = qty
                            new_list.append(ele)
            vals['order_line'] = new_list
            months = [('1', 'January'),('2', 'February'),('3', 'March'),('4', 'April'),('5', 'May'),('6', 'June'),('7', 'July'),('8', 'August'), ('9', 'September'),('10', 'October'), ('11', 'November'), ('12', 'December')]
            month_name = dict(months).get(vals.get('month'))
            vals['name'] = 'Mestengido - %s - %s' % (month_name,vals.get('year'))
            vals['squ'] = self.env['ir.sequence'].next_by_code('mest.mest') or _('New')
            
     
        res = super(MestengidoOrder, self).create(vals)
        return res





class MestengidoOrderLines(models.Model):
    _name = 'mest.order.lines'
    _description = 'Mestengido Order Lines'
    _order = 'order_id, sequence, id'

    @api.onchange('product_qty','price_unit')
    def _compute_total_price(self):
        """
        Compute the price unit   of each product.
        """
        amount_total = values = 0.0
        PO = self.env['mest.order'].search([('id','in',self.order_id.ids)])
        _logger.info("PO:%s",PO.order_line)
        total = 0.0
        vals = {}
        for line in self:
            # vals['total_price'] = float(line.product_qty * line.price_unit)
            total += line.total_price
            _logger.info(total)
            _logger.info("Vals:%s",vals)
            if line.product_qty  and line.price_unit is not None:
                line.total_price = float(line.product_qty) * float(line.price_unit)
               
            else:
                line.total_price = 0
   


    name = fields.Text(string='Description')
    sequence = fields.Integer(
        help="Gives the sequence of this line when displaying the Mestengido request.",
        default=1,
        string="S.No"
    )
    sequence2 = fields.Integer(
        help="Shows the sequence of this line in the Mestengido order.",
        related='sequence',
        string="No",
        readonly=True,
        store=True
    )
    product_qty = fields.Integer(string='Quantity', digits='Product Unit of Measure',force_save="1")
    product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty')
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True)
    product_type = fields.Selection(related='product_id.type', readonly=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price',force_save="1")
    total_price = fields.Float(string='Total Price', digits='Total Price', force_save="1")
    sub_total_price = fields.Float(string='Sub Total Price', digits='Total Price')
    order_id = fields.Many2one('mest.order', string='Request Reference', index=True,  ondelete='cascade')


    @api.model
    def create(self, values):
        line = super(MestengidoOrderLines, self).create(values)
        if self.env.context.get('keep_line_sequence'):
            line.order_id._reset_sequence()
        return line
    
    @api.depends('order_line')
    def _chech_value(self):
        _logger.info(self.sequence2)
        _logger.info(self.product_id.name)
        _logger.info(len(self.product_id))
        sale_order = self.env['sale.order'].sudo().search([('state','like','draft')])
        _logger.info(sale_order)
        if self.product_id != False:
            for l in range(len(sale_order)):
                for line in sale_order.order_line:
                    _logger.info(line.product_id)
