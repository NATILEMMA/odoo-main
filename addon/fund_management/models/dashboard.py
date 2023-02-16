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

class CurrentBalanceReport(models.Model):
    _name = "current.balance.report"
    _description = "Manager Balance Report"
    _auto = False
    _rec_name = 'receiver_id'


    receiver_id = fields.Many2one('hr.employee', string="Manager", domain=[('is_fund_mgr','=',True)], readonly=True)

    amount = fields.Float(string='Current Balance')        
    
    _order = 'amount asc'

    def create(self, vals):
        """
        Method to return Employee Nos.based on gender
        """
        tools.drop_view_if_exists(vals, self._table)
        vals.execute("""CREATE or REPLACE VIEW %s as (
        	SELECT temp.id as id, temp.id as receiver_id,  (COALESCE(temp.paidamt ,0 ) - COALESCE(temp.expamt , 0) ) as amount FROM (
			SELECT he.id,
			(SELECT sum(fc.amount) as fca FROM fund_collection as fc WHERE fc.receiver_id = he.id AND fc.state='paid') as paidamt,
			(SELECT sum(fex.expense_amount) as fca FROM fund_expense as fex WHERE fex.spender = he.id AND fex.state='expense') as expamt
			FROM  hr_employee as he where he.is_fund_mgr = True) as temp
            )""" % (self._table))

