from tokenize import group
from odoo import api, fields, models
from odoo.exceptions import UserError



class Contract(models.Model):
    _inherit = "hr.contract"