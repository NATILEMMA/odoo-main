from odoo import fields,models , api
from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging
from odoo.exceptions import UserError ,ValidationError

_logger = logging.getLogger(__name__)
class estate_property_offer(models.Model):
    _name = "estate.property.offer"
    _log_access = True
    price = fields.Float(string="Price")
    status = fields.Selection(string = "Status",copy = False,selection=[('accepted', 'Accepted'), ('refused', 'Refused')])
    partner_id = fields.Many2one("res.partner",required = True,string="partner")
    property_id = fields.Many2one("estate.property",requiered  = True)
    validity = fields.Integer(string = 'Validity',default = 7,readonly = False)
    date_deadline = fields.Datetime(compute = "_date_deadline_calculator",inverse= "_validity_calculator", string="Date Deadline",readonly = False)
    
    _sql_constraints = [('offer_price_constraint','check(price > 0 )','A property offer price must be strictly positive')]
    
    _order = "price desc"


    @api.constrains('property_id.expected_price', 'price')
    def _check_price_percentage_relative_to_expected_price(self):
        for record in self:
            if record.property_id.expected_price:
                if record.price < (record.property_id.expected_price * 0.9):
                    raise ValidationError("Fields name and description must be different")
    def action_accept_offer(self):
        for record in self :
            if record.status == "refused":
                raise UserError("offer already refused try another time")
            else:
                record.status = "accepted"
                record.property_id.selling_price = record.price
                record.property_id.buyer_id = record.partner_id


    def action_refuse_offer(self):
        for record in self:
            if record.status == "accepted":
                raise UserError("offer already accepted")
            else:
                record.status = "refused"
               

    @api.depends('validity','create_date')
    def _date_deadline_calculator(self):
        for record in self:
            if record.create_date:
                record.date_deadline =  record.create_date + relativedelta(days= record.validity)
            else:
                record.date_deadline = ''

    @api.depends('date_deadline', 'create_date')
    def _validity_calculator(self):
        for record in self:
            if record.date_deadline and record.create_date :
                record.validity = int((record.date_deadline - record.create_date).days)

    @api.model
    def create(self,vals):
        price = self.price 

        if self.env['estate.property'].browse(vals['property_id']).expected_price  != 0 and self.env['estate.property'].browse(vals['property_id']).expected_price > price:
          raise UserError("price is lower than expected price") 

        self.env['estate.property'].browse(vals['property_id']).state = "offer_received"
        return super().create(vals)

