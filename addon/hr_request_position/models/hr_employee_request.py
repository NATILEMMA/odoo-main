from datetime import date
import datetime
from tokenize import group
from odoo import api, fields, models
from odoo.exceptions import UserError
import os

REQUEST_STATES = [
    ('draft', 'Draft'),
    ('in_progress', 'Requested'),
    ('hr_approval', 'Hr Approval' ),
    ('manager_approval', 'Manager Approval' ),
    ('rejected', 'Rejected'),
    ('closed', 'Closed')
]

REQUEST_TYPE = [
    ('salary_request', 'Salary Request'),
    ('position_request', 'Job Position Request')
]

class HrEmployeeRequest(models.Model):
    _name = 'hr.employee.position.request'
    _description = 'Employees Position Request'


    

    reference_no = fields.Char(string='Request Document Reference', required=True,
                          readonly=True, default='New', index=True)
    employee_id = fields.Many2one('hr.employee', string="Company employee", required=True)
    job_title = fields.Char(related='employee_id.job_title', related_sudo=False, tracking=True)
    work_phone = fields.Char(related='employee_id.work_phone', related_sudo=False, tracking=True)
    work_email = fields.Char(related='employee_id.work_email', related_sudo=False, tracking=True)
    department_id = fields.Many2one(related='employee_id.department_id', readonly=False, related_sudo=False, tracking=True)
    work_location = fields.Char(related='employee_id.work_location', related_sudo=False, tracking=True)
    employee_parent_id = fields.Many2one('hr.employee',related='employee_id.parent_id', string='Manager', related_sudo=False, tracking=True)
    coach_id = fields.Many2one('hr.employee', related='employee_id.coach_id', string='Coach',related_sudo=False, tracking=True)
    state = fields.Selection(REQUEST_STATES,
                              'Status', tracking=True,
                              copy=False, default='draft')
    contract_id = fields.Many2one('hr.contract',related='employee_id.contract_id', string='Current Contract', help='Current contract of the employee', related_sudo=False, tracking=True)
    job_id = fields.Many2one('hr.job', 'Job Position')
    hr_responsible_user_id = fields.Many2one('res.users', related='contract_id.hr_responsible_id',tracking=True,
        help='Person responsible for validating the employee\'s contracts.')

    user_id = fields.Many2one('res.users')
    requested_position = fields.Many2one('hr.job','Requested Job Position')
    requested_department = fields.Many2one('hr.department', 'Requested Department')
    attachment = fields.Binary(string="Upload Attachment file", required=True)
    attachment_name = fields.Char(string='File Name')
    note = fields.Text('Notes')
    period = fields.Char('Period', compute="_compute_period")
    company_id = fields.Many2one('res.company', string=  'Company',default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', related='contract_id.currency_id', readonly=True)
    estimated_salary = fields.Monetary(string='Estimated Salary', help="Employee's monthly gross wage.", 
    groups= "hr_request_position.group_request_hr_approval,hr_request_position.group_request_manager_approval")
    wage = fields.Monetary(related='contract_id.wage', related_sudo=False, tracking=True,
    groups= "hr_request_position.group_request_hr_approval,hr_request_position.group_request_manager_approval")
    salary_or_position = fields.Selection(REQUEST_TYPE,
                              'Request Type', tracking=True, required=True,
                              copy=False, default='position_request')


    @api.model
    def create(self, vals):
        contract = self.env['hr.contract'].search([('employee_id', '=', vals['employee_id'])], limit=1)
        if vals['salary_or_position'] == 'position_request':
            if vals['requested_position'] == self.contract_id.job_id or vals['requested_department'] ==  self.department_id:
                raise UserError(('Already in Position'))

            vals['state'] = 'in_progress'
            vals['reference_no'] = self.env['ir.sequence'].next_by_code('hr.employee.position.request')
            request = super(HrEmployeeRequest, self).create(vals)
    
        elif vals['salary_or_position'] == 'salary_request':
            if vals.get('estimated_salary') != None:
                if vals.get('estimated_salary') <= contract.wage:
                    raise UserError(('Please correct your estimation on provided salary'))
                else:
                    vals['state'] = 'in_progress'
                    vals['reference_no'] = self.env['ir.sequence'].next_by_code('hr.employee.position.request')
                    request = super(HrEmployeeRequest, self).create(vals)
            else:
                vals['state'] = 'in_progress'
                vals['reference_no'] = self.env['ir.sequence'].next_by_code('hr.employee.position.request')
                request = super(HrEmployeeRequest, self).create(vals)

        return request

    def button_request(self):
        self.write({'state':'in_progress'})

    def write(self, vals):
        res = super(HrEmployeeRequest, self).write(vals)
        return res
        

    def hr_button_approve(self):

        contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)], limit=1)
        if self.salary_or_position == 'salary_request':
            if self.estimated_salary <= contract.wage:
                raise UserError(('Please correct your estimation on provided salary'))
            else:
                self.write({'state':'hr_approval'})
        
        elif self.salary_or_position == 'position_request':
            self.write({'state':'hr_approval'})

    def manager_button_approve(self):
        if self.salary_or_position == 'position_request':
            approved_contract = self.contract_id
            self.contract_id.job_id = self.requested_position
            self.contract_id.department_id = self.requested_department
            self.department_id = self.requested_department
            self.job_title = self.requested_position.name
            self.employee_id.job_title = self.job_title 
            self.write({'state':'manager_approval'})
        
        elif self.salary_or_position == 'salary_request':
            self.wage = self.estimated_salary
            self.write({'state':'manager_approval'})

    def button_reject(self):
        self.write({'state':'rejected'})

    def button_set_draft(self):
        print('x')
        self.write({'state':'draft'})

    @api.depends("contract_id")
    def _compute_period(self):
        fmt = '%Y-%m-%d'
        start_date = self.contract_id.date_start
        dateStr = start_date.strftime(fmt)
        end_date = datetime.date.today().strftime('%Y-%m-%d')
        d1 = datetime.datetime.strptime(dateStr, fmt)
        d2 = datetime.datetime.strptime(end_date, fmt)
        # self.period = (d2 - d1).days
        if (d2 - d1).days <= 365:
            self.period = 1
        else:
            self.period = (d2 - d1).days // 365


    


    