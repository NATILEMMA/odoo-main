import logging
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tokenize import group
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import os
from odoo.exceptions import UserError, Warning, ValidationError
import re
import base64
import requests
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)

class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    budget_line = fields.One2many('budget.lines', 'analytic_account_id', 'Budget Lines')
    department_id = fields.Many2one('hr.department','Department')
    budget_analytic_account = fields.Boolean(default=False)
    is_allowed = fields.Boolean("Is_allowed", default=False)



class Employee(models.Model):
    _inherit = 'hr.employee'

    is_allowed = fields.Boolean("Is_allowed", default=False)
    accountAnalytic = fields.Many2one('account.analytic.account')

class HrExpense(models.Model):

    _inherit = "hr.expense"

    

    @api.model
    def create(self, vals):
        _logger.info("############ Expensse vals:%s",vals)
        _logger.info(vals['analytic_account_id'])
        user = self.env['res.users'].search([('id','=',self.env.uid)])
        employee_id = user.employee_id
        _logger.info(employee_id.name)
        _logger.info("Employee Name %s",employee_id.is_allowed)
        employee_id = self.env['hr.employee'].search([('id','=',employee_id.id)])
        AccountAnalytic = self.env['account.analytic.account'].search([('id','=',vals['analytic_account_id'])], limit=1)
        budget = self.env['budget.planning'].search([('analytic_account_id','=',AccountAnalytic)], limit=1)
        fiscal_year = self.env['fiscal.year'].search([('state','=','active')],limit=1)
        _logger.info("EMploAccountAnalytic :%s",employee_id.accountAnalytic)
        _logger.info("AccountAnalytic :%s",AccountAnalytic.id)

        _logger.info(AccountAnalytic.budget_analytic_account)

        # try:
        if AccountAnalytic.is_allowed:
            
            if AccountAnalytic.budget_analytic_account == True:
                if  employee_id.is_allowed == True and employee_id.accountAnalytic.id == AccountAnalytic.id: #AccountAnalytic.department_id == employee_id.department_id and
                    _logger.info("$$$$$$")
                    if len(fiscal_year) > 0:
                        if str(budget.date_from) < vals['date'] < str(budget.date_to):
                            pass
                            # raise Warning("passed")
                        else:
                            raise Warning("Choose the appropriate budget fiscal date")
                    else:
                        raise UserError(_('Fiscal year of the system is not set.'))

                else:
                    raise UserError(_('You are not authorized to use this budget account.'))

            if AccountAnalytic.budget_analytic_account == False:
                if len(fiscal_year) > 0:
                    if str(budget.date_from) < vals['date'] < str(budget.date_to):
                        pass
                        # raise Warning("passed")
                    else:
                        raise Warning("Choose the appropriate budget fiscal date")
                else:
                    raise UserError(_('Fiscal year of the system is not set.'))
        else:
            raise UserError(_('This Account are not Approved.'))
        # except:
        #     raise UserError(_('Fiscal year of the system is not set.'))


            # raise Warning("Your Are  Allowed For This Budget Account")
        return super(HrExpense, self).create(vals)


    def write(self, vals):
        _logger.info("############ Expense Update:%s",vals)
        user = self.env['res.users'].search([('id','=',self.env.uid)])
        employee_id = user.employee_id
        _logger.info(employee_id)
        _logger.info(self.ids)
        _logger.info("Employee Name %s",employee_id.is_allowed)

        try:
            fiscal_year = self.env['fiscal.year'].search([('state','=','active')],limit=1)
          
            if str(fiscal_year.date_from) < vals['date'] < str(fiscal_year.date_to):
                pass
                # raise Warning("passed")
            else:
                raise Warning("Choose the appropriate fiscal date")
            

            # raise Warning("Your Are  Allowed For This Budget Account")
        except:
            pass
            
        return super(HrExpense, self).write(vals)

