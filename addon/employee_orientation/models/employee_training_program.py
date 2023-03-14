from odoo import api, fields, models, _


class Trianing(models.Model):

    _name = "employee.training.program"
    _description = "Type of training for employees"


    name = fields.Char( String = 'name',required=True)
    description = fields.Char(string="description")