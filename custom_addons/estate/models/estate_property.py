from odoo import fields, models

class estate_property(models.Model):
    _name='estate.property.type'
    _description = 'this is a real estate type '

    name = fields.Char(string = 'Name',required = True)
    _sql_constraints = [('unique_name','unique(name)',' A property type name must be unique')]
    property_ids = fields.One2many("estate.property","property_type_id")
    sequence = fields.Integer('sequence' , default = 1,help="this is used to order stages")
    _order = "sequence, name"




