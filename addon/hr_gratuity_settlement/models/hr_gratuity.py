# -*- coding: utf-8 -*-
from datetime import date
from odoo import fields, models, api, _
from odoo.exceptions import Warning, UserError


class EmployeeGratuity(models.Model):
    _name = 'hr.gratuity'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Gratuity"


    def _calculate_wages(self, daily_wage):
        """This function will calculate the wages for different Severance types"""
        gratuity_pay_per_year = 0.0
        base_severance = self.env['hr.gratuity.accounting.configuration'].search([('name', '=', 'Basic')])
        total_days_remaining = (self.total_working_months * 30) + self.total_working_days
        base_year = daily_wage * base_severance.gratuity_configuration_table.percentage
        base_less_than_year = (base_year * total_days_remaining) / 365 
        base_more_than_year = (1/3 * (daily_wage * base_severance.gratuity_configuration_table.percentage) * (self.total_working_years - 1)) + \
                              ((1/3 * (daily_wage * base_severance.gratuity_configuration_table.percentage) * total_days_remaining) / 365) + \
                              daily_wage * base_severance.gratuity_configuration_table.percentage

        if not self.employee_gratuity_configuration.add_to_base:
            if len(self.employee_gratuity_configuration.gratuity_configuration_table.ids) != 1:
                raise Warning(_('Please Make This Configuration To Only Have 1 Rule'))
            self.extra_severance = 0.00
            if self.total_working_years < 1:
               self.basic_gratuity = gratuity_pay_per_year = (daily_wage * self.employee_gratuity_duration.percentage * total_days_remaining) / 365
            elif self.total_working_years == 1:
                self.basic_gratuity = gratuity_pay_per_year = daily_wage * self.employee_gratuity_duration.percentage
            else:
                self.basic_gratuity = gratuity_pay_per_year = (1/3 * (daily_wage * self.employee_gratuity_duration.percentage) * (self.total_working_years - 1)) + \
                                        ((1/3 * (daily_wage * self.employee_gratuity_duration.percentage) * total_days_remaining) / 365) + \
                                        daily_wage * self.employee_gratuity_duration.percentage
        else:
            if len(self.employee_gratuity_configuration.gratuity_configuration_table.ids) != 2:
                raise Warning(_('Please Make This Configuration To Only Have 2 Rules'))
            self.extra_severance = daily_wage * self.employee_gratuity_duration.percentage
            if self.total_working_years < 1:
                self.basic_gratuity = base_less_than_year
                gratuity_pay_per_year = self.basic_gratuity + self.extra_severance
            elif self.total_working_years == 1:
                self.basic_gratuity = base_year
                gratuity_pay_per_year = self.basic_gratuity + self.extra_severance
            else:
                self.basic_gratuity = base_more_than_year
                gratuity_pay_per_year = self.basic_gratuity + self.extra_severance
        return gratuity_pay_per_year


    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled'),
        ('expensed', 'Expensed')],
        default='draft', track_visibility='onchange')
    name = fields.Char(string='Reference', required=True, copy=False,
                       readonly=True,
                       default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  required=True, help="Employee")
    employee_contract_type = fields.Selection([
        ('limited', 'Limited'),
        ('unlimited', 'Unlimited')], string='Contract Type', readonly=True,
        store=True, help="Choose the contract type."
                         "if contract type is limited then during gratuity settlement if you have not specify the end date for contract, gratuity configration of limited type will be taken or"
                         "if contract type is Unlimited then during gratuity settlement if you have specify the end date for contract, gratuity configration of limited type will be taken.")
    employee_joining_date = fields.Date(string='Joining Date', readonly=True,
                                        store=True, help="Employee joining date")
    wage_type = fields.Selection([('monthly', 'Monthly Fixed Wage'), ('hourly', 'Hourly Wage')],
                                 help="Select the wage type monthly or hourly")
    total_working_days = fields.Integer(string="Total Days Remaining", readonly=True, store=True, help="Total Remaining Days")
    total_working_months = fields.Integer(string="Total Months Remaining", readonly=True, store=True, help="Total Remaining Months")
    total_working_years = fields.Integer(string='Total Years Worked', readonly=True, store=True, help="Total working years")
    employee_probation_years = fields.Float(string='Leaves Taken(Years)', readonly=True, store=True,
                                            help="Employee probation years")
    employee_remaining_leaves = fields.Float(related="employee_id.remaining_leaves", string="Remaining Leaves", readonly=True, store=True)
    employee_gratuity_years = fields.Float(string='Gratuity Calculation Years',
                                           readonly=True, store=True, help="Employee gratuity years")
    employee_basic_salary = fields.Float(string='Basic Salary',
                                         readonly=True,
                                         help="Employee's basic salary.")
    employee_gratuity_duration = fields.Many2one('gratuity.configuration',
                                                 readonly=True,
                                                 string='Configuration Line')
    employee_gratuity_configuration = fields.Many2one('hr.gratuity.accounting.configuration', domain="[('name', '!=', 'Basic')]",
                                                      required=True,
                                                      string='Gratuity Configuration')
    basic_gratuity = fields.Float(string="Basic Gratuity", readonly=True, store=True, default=0.00)
    extra_severance = fields.Float(string="Extra Severance", readonly=True, store=True, default=0.00)
    payment_for_leaves = fields.Float(string="Remaining Leaves Payments", readonly=True, store=True, default=0.00)
    employee_gratuity_amount = fields.Float(string='Gratuity Payment', readonly=True, store=True,
                                            help="Gratuity amount for the employee. \it is calculated If the wage type is hourly then gratuity payment is calculated as employee basic salary * Employee Daily Wage Days * gratuity configration rule percentage * gratuity calculation years.orIf the wage type is monthly then gratuity payment is calculated as employee basic salary * (Working Days/Employee Daily Wage Days) * gratuity configration rule percentage * gratuity calculation years.")
    corrected_employee_gratuity_amount = fields.Float(string="Corrected Gratuity Payment", readonly=True, store=True, default=0.00)
    correction_amount_flag = fields.Boolean(default=False)
    hr_gratuity_credit_account = fields.Many2one('account.account', help="Gratuity credit account")
    hr_gratuity_debit_account = fields.Many2one('account.account', help="Gratuity debit account")
    hr_gratuity_journal = fields.Many2one('account.journal', help="Gratuity journal")
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.company, help="Company")
    currency_id = fields.Many2one(related="company_id.currency_id",
                                  string="Currency", readonly=True, help="Currency")

    @api.model
    def create(self, vals):
        """ assigning the sequence for the record """
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.gratuity')
        return super(EmployeeGratuity, self).create(vals)

    @api.depends('employee_id')
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """ calculating the gratuity pay based on the contract and gratuity
        configurations """
        if self.employee_id.id:
            current_date = date.today()
            probation_ids = self.env['hr.training'].search([('employee_id', '=', self.employee_id.id)])
            contract_ids = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
            contract_sorted = contract_ids.sorted(lambda line: line.date_start)
            if not contract_sorted:
                raise Warning(_('No contracts found for the selected employee...!\n'
                                'Employee must have at least one contract to compute gratuity settelement.'))
            self.employee_joining_date = joining_date = contract_sorted[0].date_start
            employee_probation_days = 0
            # find total probation days
            for probation in probation_ids:
                start_date = probation.start_date
                end_date = probation.end_date
                employee_probation_days += (end_date - start_date).days
            # get running contract
            hr_contract_id = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
            if len(hr_contract_id) > 1 or not hr_contract_id:
                raise Warning(_('Selected employee have multiple or no running contracts!'))

            self.wage_type = hr_contract_id.wage_type
            if self.wage_type == 'hourly':
                self.employee_basic_salary = hr_contract_id.hourly_wage
            else:
                self.employee_basic_salary = hr_contract_id.wage

            if hr_contract_id.date_end:
                self.employee_contract_type = 'limited'
                days = (hr_contract_id.date_end - joining_date).days
                self.total_working_years, days = days // 365, days % 365
                self.total_working_months, days = days // 30, days % 30
                self.total_working_days = days
                self.employee_probation_years = employee_probation_days / 365
                employee_gratuity_years = (days - employee_probation_days) / 365
                self.employee_gratuity_years = employee_gratuity_years
            else:
                raise Warning(_("Please Add A Termination Date To Your Employee's Contract!"))


    @api.depends('employee_gratuity_configuration')
    @api.onchange('employee_gratuity_configuration')
    def _onchange_employee_gratuity_configuration(self):
        """This function will get gratuity configration from hr_accounting_gratuity_configuration"""
        names = self.employee_gratuity_configuration.gratuity_configuration_table.mapped('name')
        for name in names:
            if name[:3] != 'Base':
                config = self.env['gratuity.configuration'].search([('name', '=', name), ('gratuity_accounting_configuration_id', '=', self.employee_gratuity_configuration.id)])
                self.employee_gratuity_duration = config
        if self.employee_gratuity_configuration.name == "Retired" and (self.employee_gratuity_duration.from_year > self.total_working_years):
            raise Warning(_('Selected Employee Has Been Working For Less Than 5 Years And Is Not Eligible For Retirement Settlement'))
        self.hr_gratuity_journal = self.employee_gratuity_configuration.gratuity_journal.id
        self.hr_gratuity_credit_account = self.employee_gratuity_configuration.gratuity_credit_account.id
        self.hr_gratuity_debit_account = self.employee_gratuity_configuration.gratuity_debit_account.id

        if self.employee_gratuity_duration and self.wage_type == 'hourly':
            if self.employee_gratuity_duration.employee_working_days != 0:
                if self.employee_id.resource_calendar_id and self.employee_id.resource_calendar_id.hours_per_day:
                    daily_wage = self.employee_basic_salary * self.employee_id.resource_calendar_id.hours_per_day
                else:
                    daily_wage = self.employee_basic_salary * 8
                self.payment_for_leaves = self.employee_remaining_leaves * daily_wage
                employee_gratuity_amount = self._calculate_wages(daily_wage) + self.payment_for_leaves
                self.employee_gratuity_amount = round(employee_gratuity_amount, 2)
                if self.employee_gratuity_amount > (self.employee_basic_salary * 12):
                    self.correction_amount_flag = True
                    self.corrected_employee_gratuity_amount = self.employee_basic_salary * 12
                else:
                    self.correction_amount_flag = False
            else:
                raise Warning(_("Employee working days is not configured in "
                                "the gratuity configuration..!"))
        elif self.employee_gratuity_duration and self.wage_type == 'monthly':
            if self.employee_gratuity_duration.employee_daily_wage_days != 0:
                daily_wage = self.employee_basic_salary / self.employee_gratuity_duration.employee_daily_wage_days
                self.payment_for_leaves = self.employee_remaining_leaves * daily_wage
                employee_gratuity_amount = self._calculate_wages(daily_wage) + self.payment_for_leaves
                self.employee_gratuity_amount = round(employee_gratuity_amount, 2)
                if self.employee_gratuity_amount > (self.employee_basic_salary * 12):
                    self.correction_amount_flag = True
                    self.corrected_employee_gratuity_amount = self.employee_basic_salary * 12
                else:
                    self.correction_amount_flag = False
            else:
                raise Warning(_("Employee wage days is not configured in "
                                "the gratuity configuration..!"))

    # Changing state to submit
    def submit_request(self):
        self.write({'state': 'submit'})

    # Canceling the gratuity request
    def cancel_request(self):
        self.write({'state': 'cancel'})

    # Set the canceled request to draft
    def set_to_draft(self):
        self.write({'state': 'draft'})

    # function for creating the account move with gratuity amount and
    # account credentials
    def approved_request(self):
        for hr_gratuity_id in self:
            debit_vals = {
                'name': hr_gratuity_id.employee_id.name,
                'account_id': hr_gratuity_id.hr_gratuity_debit_account.id,
                'partner_id': hr_gratuity_id.employee_id.address_home_id.id or False,
                'journal_id': hr_gratuity_id.hr_gratuity_journal.id,
                'date': date.today(),
                'debit': hr_gratuity_id.employee_gratuity_amount > 0.0 and hr_gratuity_id.employee_gratuity_amount or 0.0,
                'credit': hr_gratuity_id.employee_gratuity_amount < 0.0 and -hr_gratuity_id.employee_gratuity_amount or 0.0,
            }
            credit_vals = {
                'name': hr_gratuity_id.employee_id.name,
                'account_id': hr_gratuity_id.hr_gratuity_credit_account.id,
                'partner_id': hr_gratuity_id.employee_id.address_home_id.id or False,
                'journal_id': hr_gratuity_id.hr_gratuity_journal.id,
                'date': date.today(),
                'debit': hr_gratuity_id.employee_gratuity_amount < 0.0 and -hr_gratuity_id.employee_gratuity_amount or 0.0,
                'credit': hr_gratuity_id.employee_gratuity_amount > 0.0 and hr_gratuity_id.employee_gratuity_amount or 0.0,
            }
            vals = {
                'name': hr_gratuity_id.name + " - " + 'Gratuity for' + ' ' + hr_gratuity_id.employee_id.name,
                'narration': hr_gratuity_id.employee_id.name,
                'ref': hr_gratuity_id.name,
                'partner_id': hr_gratuity_id.employee_id.address_home_id.id or False,
                'journal_id': hr_gratuity_id.hr_gratuity_journal.id,
                'date': date.today(),
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)],
            }
            move = hr_gratuity_id.env['account.move'].create(vals)
            move.post()
        self.write({'state': 'approve'})


class EmployeeContractWage(models.Model):
    _inherit = 'hr.contract'

    # structure_type_id = fields.Many2one('hr.payroll.structure.type', string="Salary Structure Type")
    company_country_id = fields.Many2one('res.country', string="Company country", related='company_id.country_id',
                            readonly=True)
    wage_type = fields.Selection([('monthly', 'Monthly Fixed Wage'), ('hourly', 'Hourly Wage')])
    hourly_wage = fields.Monetary('Hourly Wage', digits=(16, 2), default=0, required=True, tracking=True,
                                  help="Employee's hourly gross wage.")
