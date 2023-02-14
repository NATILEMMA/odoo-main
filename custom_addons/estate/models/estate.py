from odoo import fields, models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError


class estate(models.Model):
    _name = 'estate.property'
    _description = 'this is a real estate '

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description', )
    postcode = fields.Char(string='Postcode', )
    date_availability = fields.Date(string='Date Available', copy=False,
                                    default=datetime.now() + relativedelta(months=3))
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer(string='bedrooms', default=2)
    living_area = fields.Integer(string='living Area')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    garden = fields.Boolean(string='Garden')
    garden_area = fields.Integer(string='garden Area')
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('south', 'South'), ('east', 'East'), ('west', 'West'), ('north', 'North')]
    )
    state = fields.Selection(
        string='state',
        default="new",
        copy=False,
        required=True,
        selection=[('new', 'New'), ('offer_received', 'Offer Received'), ('offer_accepted', 'Offer Accepted'),
                   ('sold', 'Sold'), ('canceled', 'Canceled')]
    )
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    sales_person_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    tag_ids = fields.Many2many("estate.property.tag")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="offer")
    total_area = fields.Integer(compute="_compute_total_area", string="Total Area(sqrm)")
    best_price = fields.Float(string="best price", compute="_compute_max_offer")
    
    _sql_constraints = [('expected_price_constraint','check(expected_price > 0 )','A property expected price must be strictly positive'),('selling_price_constraint','check(selling_price > 0 )',' A property selling price must be positive')]

    
    def action_sell(self):
        for record in self:
            if record.state == 'sold':
                raise UserError('Property already sold')
            elif record.state == "canceled":
                raise UserError('Property already sold')
            else:
                record.state = 'sold'
        return True

    def action_cancel(self):
        for record in self:
            if record.state == "canceled":
                raise UserError('Property already canceled')
            elif record.state == "sold":
                raise UserError('Property already sold')
            else:
                record.state = 'canceled'
        return True

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "south"
        else:
            self.garden_area = 0
            self.garden_orientation = ""

    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            if record.living_area or record.garden_area:
                record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_max_offer(self):
        for record in self:
            if record.offer_ids.mapped('price'):
                record.best_price = max(record.offer_ids.mapped('price'))
    
    def unlink(self):
        if any((record.state == "new" or record.state == "cancled") for record in self):
            raise UserError("Can't delete an property if its not new or cancled!")
    

