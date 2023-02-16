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

class GenerateDuesWizard(models.TransientModel):
    
    _name = 'generate.dues.wizard'

    month = fields.Selection(
        [('1', 'January'), 
        ('2', 'February'), 
        ('3', 'March'), 
        ('4', 'April'),
        ('5', 'May'), 
        ('6', 'June'), 
        ('7', 'July'),
        ('8', 'August'), 
        ('9', 'September'),
        ('10', 'October'), 
        ('11', 'November'), 
        ('12', 'December')], 'Month', required=True)
    
    @api.model
    def year_selection(self):
        year = 2000 # replace 2000 with your a start year
        year_list = []
        while year != 2030: # replace 2030 with your end year
            year_list.append((str(year), str(year)))
            year += 1
        return year_list


    amount= fields.Float('Amount', required=True)
    year = fields.Selection(
        year_selection,
        string="Year",
        default="2015", # as a default value it would be 2019)
    )

    @api.model
    def generate_dues(self):

        if self.amount == 0:
            raise Warning('Amount Cannot be Zero.')

        employee_ids = self.env['hr.employee'].search([])

        for employee in employee_ids:
            vals = {'employee_id':employee.id, 'month': self.month , 'year': self.year, 'state':'draft', 'amount':self.amount}
            res = self.env['fund.collection'].create(vals)

        return 

