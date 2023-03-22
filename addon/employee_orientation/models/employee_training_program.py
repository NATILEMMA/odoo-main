from odoo import api, fields, models, _


class Trianing(models.Model):

    _name = "employee.training.program"
    _description = "Type of training for employees"
    


    name = fields.Char( String ='Name',required=True)
    training_round_ids = fields.Many2many('employee.training.program.round', string="Training rounds")
    description = fields.Char(string="description")


