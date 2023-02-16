
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tokenize import group
from odoo.exceptions import UserError
import os
from odoo.exceptions import UserError, Warning, ValidationError
import re
import base64
import requests
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)


class AccountBudgetPost(models.Model):
    _name = "account.budget.post"
    _order = "name"
    _description = "Budgetary Position"

    name = fields.Char('Name', required=True)
    account_ids = fields.Many2many('account.account', 'account_budget_rel', 'budget_id', 'account_id', 'Accounts',
                                   domain=[('deprecated', '=', False)])
    budget_line = fields.One2many('budget.lines', 'general_budget_id', 'Budget Lines')
    

    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'account.budget.post'))

    def _check_account_ids(self, vals):
        if 'account_ids' in vals:
            account_ids = self.resolve_2many_commands('account_ids', vals['account_ids'])
        else:
            account_ids = self.account_ids
        if not account_ids:
            raise ValidationError(_('The budget must have at least one account.'))

    @api.model
    def create(self, vals):
        self._check_account_ids(vals)
        return super(AccountBudgetPost, self).create(vals)

    def write(self, vals):
        self._check_account_ids(vals)
        return super(AccountBudgetPost, self).write(vals)


class Budget(models.Model):
    _name = "budget.budget"
    _description = "Budget"
    _inherit = ['mail.thread']

    name = fields.Char('Budget Name', required=True, states={'done': [('readonly', True)]})
    creating_user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    date_from = fields.Date('Start Date', required=True, states={'done': [('readonly', True)]})
    date_to = fields.Date('End Date', required=True, states={'done': [('readonly', True)]})
    budget_usage = fields.Char('Budget Usage')
    planned_amount = fields.Float('Total Planned Amount', digits=0)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('done', 'Done')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    budget_line = fields.One2many('budget.lines', 'budget_id', 'Budget Lines',
                                  states={'done': [('readonly', True)]}, copy=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'account.budget.post'))

    def action_budget_confirm(self):
        self.write({'state': 'confirm'})

    def action_budget_draft(self):
        self.write({'state': 'draft'})

    def action_budget_validate(self):
        self.write({'state': 'validate'})

    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    def action_budget_done(self):
        self.write({'state': 'done'})


class BudgetLines(models.Model):
    _name = "budget.lines"
    _rec_name = "budget_id"
    _description = "Budget Line"

    budget_id = fields.Many2one('budget.budget', 'Budget', ondelete='cascade', index=True, required=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position', required=True)
    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)
    paid_date = fields.Date('Paid Date')
    original_planned_amount = fields.Float('Original Planned Amount', digits=0)
    reserved_amount = fields.Float('Reserved Amount', compute='_compute_reserved_amount', digits=0)
    budget_usage = fields.Char('Budget Usage',compute='_compute_budget_percentage', default="0%")
    department_id = fields.Many2one('hr.department','Department')
    commitment = fields.Float('Commitment', digits=0)
    available_amount = fields.Float('Available Amount', digits=0)

    planned_amount = fields.Float('Planned Amount', required=True, digits=0)
    practical_amount = fields.Float(compute='_compute_practical_amount', string='Practical Amount', digits=0)
    theoretical_amount = fields.Float(compute='_compute_theoretical_amount', string='Theoretical Amount', digits=0)
    percentage = fields.Float(compute='_compute_percentage', string='Achievement')
    company_id = fields.Many2one(related='budget_id.company_id', comodel_name='res.company',
                                 string='Company', store=True, readonly=True)

    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            if line.analytic_account_id.id:
                self.env.cr.execute("""
                    SELECT SUM(amount)
                    FROM account_analytic_line
                    WHERE account_id=%s
                        AND date between %s AND %s
                        AND general_account_id=ANY(%s)""",
                                    (line.analytic_account_id.id, date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = result



    def _compute_reserved_amount(self):
        for line in self:
            if line.planned_amount != 0.00:
                line.reserved_amount = float((line.practical_amount ) + line.planned_amount)
            else:
                line.reserved_amount = 0.00



    def _compute_theoretical_amount(self):
        today = fields.Datetime.now()
        for line in self:
            # Used for the report

            if self.env.context.get('wizard_date_from') and self.env.context.get('wizard_date_to'):
                date_from = fields.Datetime.from_string(self.env.context.get('wizard_date_from'))
                date_to = fields.Datetime.from_string(self.env.context.get('wizard_date_to'))
                if date_from < fields.Datetime.from_string(line.date_from):
                    date_from = fields.Datetime.from_string(line.date_from)
                elif date_from > fields.Datetime.from_string(line.date_to):
                    date_from = False

                if date_to > fields.Datetime.from_string(line.date_to):
                    date_to = fields.Datetime.from_string(line.date_to)
                elif date_to < fields.Datetime.from_string(line.date_from):
                    date_to = False

                theo_amt = 0.00
                if date_from and date_to:
                    line_timedelta = fields.Datetime.from_string(line.date_to) - fields.Datetime.from_string(
                        line.date_from)
                    elapsed_timedelta = date_to - date_from
                    if elapsed_timedelta.days > 0:
                        theo_amt = (
                                           elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
            else:
                if line.paid_date:
                    if fields.Datetime.from_string(line.date_to) <= fields.Datetime.from_string(line.paid_date):
                        theo_amt = 0.00
                    else:
                        theo_amt = line.planned_amount
                else:
                    line_timedelta = fields.Datetime.from_string(line.date_to) - fields.Datetime.from_string(
                        line.date_from)
                    elapsed_timedelta = fields.Datetime.from_string(today) - (
                        fields.Datetime.from_string(line.date_from))

                    if elapsed_timedelta.days < 0:
                        # If the budget line has not started yet, theoretical amount should be zero
                        theo_amt = 0.00
                    elif line_timedelta.days > 0 and fields.Datetime.from_string(today) < fields.Datetime.from_string(
                            line.date_to):
                        # If today is between the budget line date_from and date_to
                        theo_amt = (
                                           elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
                    else:
                        theo_amt = line.planned_amount

            line.theoretical_amount = theo_amt

    def _compute_percentage(self):
        for line in self:
            if line.reserved_amount != 0.00:
                line.percentage = float((line.practical_amount) / line.planned_amount) * 100
            else:
                line.percentage = 0.00

    def _compute_budget_percentage(self):
        for line in self:
            if line.practical_amount != 0.00:
                percentage = (float((-(line.practical_amount)) / line.planned_amount) * 100 )
                line.budget_usage = str("%.2f" %percentage)+'  %'
                budget  = self.env['budget.budget'].search([('id','=',line.budget_id.id)])
                budget_planning  = self.env['budget.planning'].search([('name','=',budget.name)])
                _logger.info("bbbbbbbb%s",budget_planning)

                usage = 0
                value = 0
                div = len(budget.budget_line)
                _logger.info(div)
                for line2 in budget.budget_line:
                    percentage = (float((-(line2.practical_amount)) / line2.planned_amount) * 100 )
                    planned_amount = (float(line2.planned_amount))
                    usage +=  percentage
                    value += planned_amount
                    pass
                total_usage = usage / div
                _logger.info(total_usage)
                budget.budget_usage = str("%.2f" %total_usage)+'  %'
                budget.planned_amount = ("%.2f" %value)
                budget_planning.budgeted_amount = ("%.2f" %value)

                
            else:
                line.budget_usage = '0%'
                budget  = self.env['budget.budget'].search([('id','=',line.budget_id.id)])
                budget_planning  = self.env['budget.planning'].search([('name','=',budget.name)])

                usage = 0
                value = 0
                for line2 in budget.budget_line:
                    percentage = (float((-(line2.practical_amount)) / line2.planned_amount) * 100 )
                    planned_amount = (float(line2.planned_amount))
                    usage +=  percentage
                    value += planned_amount
                    pass 
                budget.budget_usage = str("%.2f" %usage)+'  %'
                budget.planned_amount = ("%.2f" %value)
                budget_planning.budgeted_amount = ("%.2f" %value)


