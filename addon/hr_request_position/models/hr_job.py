from tokenize import group
from odoo import api, fields, models
from odoo.exceptions import UserError


class Job(models.Model):
    _inherit = "hr.job"