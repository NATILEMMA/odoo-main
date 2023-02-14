
from odoo import fields, models


class estate_property_tag (models.Model):
        _name = "estate.property.tag"
        _description = "tags"

        name = fields.Char(string="Name",required = True)

        _sql_constraints = [('unique_name','unique(name)',' A property tag name  name must be unique')]
        _order = "name"