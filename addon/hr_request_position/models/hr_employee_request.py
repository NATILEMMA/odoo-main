from datetime import date
import datetime
from tokenize import group
from odoo import api, fields, models
from odoo.exceptions import UserError
import os

import logging

_logger = logging.getLogger(__name__)


REQUEST_STATES = [
    ('new', 'New'),
    ('draft', 'Draft'),
    ('in_progress', 'Requested'),
    ('hr_approval', 'HR Approved'),
    ('manager_approval', 'Manager Approved'),
    ('rejected', 'Rejected'),
]

REQUEST_TYPE = [
    ('salary_request', 'Salary Request'),
    ('position_request', 'Job Position Request')
]

class HrEmployeeRequest(models.Model):
    _name = 'hr.employee.position.request'
    _description = 'Employees Position Request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    reference_no = fields.Char(string='Request Document Reference', required=True,
                          readonly=True, default='New', index=True)
    
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id
    
    name = fields.Char( required=True,readonly=True, default='New', index=True)
    employee_id = fields.Many2one('hr.employee', string="Requested By", default=_get_employee_id,readonly=True)
    job_id = fields.Many2one(related='employee_id.job_id', related_sudo=False, tracking=True,readonly=True)
    nati = fields.Char('nati')
    work_phone = fields.Char(related='employee_id.work_phone', related_sudo=False, tracking=True,readonly=True)
    work_email = fields.Char(related='employee_id.work_email', related_sudo=False, tracking=True,readonly=True)
    department_id = fields.Many2one(related='employee_id.department_id', readonly=False, related_sudo=False, tracking=True)
    work_location = fields.Char(related='employee_id.work_location', related_sudo=False, tracking=True,readonly=True)
    employee_parent_id = fields.Many2one('hr.employee',related='employee_id.parent_id', string='Manager', related_sudo=False, tracking=True)
    coach_id = fields.Many2one('hr.employee',related='employee_id.coach_id', string='Coach',related_sudo=False, tracking=True,readonly=True)
    state = fields.Selection(REQUEST_STATES,'Status', tracking=True,copy=False,default = 'new')
    contract_id = fields.Many2one('hr.contract',string='Current Contract', compute ="_compute_contract", help='Current contract of the employee', related_sudo=False, tracking=True,readonly=True)
    current_grade_id = fields.Many2one('hr.job.grade',related='contract_id.grade_id',string = "Current job Grade")
    hr_responsible_user_id = fields.Many2one('res.users', related='contract_id.hr_responsible_id',tracking=True,help='Person responsible for validating the employee\'s contracts.',readonly=True)
    user_id = fields.Many2one('res.users')
    requested_position_id = fields.Many2one('hr.job','Requested Job Position')
    job_title = fields.Char(related='requested_position_id.name',default ='job', related_sudo=False)
    requested_department_id = fields.Many2one('hr.department', 'Requested Department')
    attachment = fields.Binary(string="Upload Attachment file")
    attachment_name = fields.Char(string='File Name')
    note = fields.Text('Notes')
    period = fields.Char('Period', compute="_compute_period")
    company_id = fields.Many2one('res.company', string=  'Company',default=lambda self: self.env.company, required=True,readonly=True)
    currency_id = fields.Many2one('res.currency', related='contract_id.currency_id', readonly=True)
    estimated_salary = fields.Monetary(string='Requested Salary', help="Employee's Requested salary.", 
    groups= "hr_request_position.group_request_hr_approval_request,hr_request_position.group_request_manager_approval")
    previous_salary = fields.Monetary(string='Prior Salary', help="Employee's salary befor salary request.", 
    groups= "hr_request_position.group_request_hr_approval_request,hr_request_position.group_request_manager_approval")
    wage = fields.Monetary(related='contract_id.wage', related_sudo=False, tracking=True,
    groups= "hr_request_position.group_request_hr_approval_request,hr_request_position.group_request_manager_approval")
    salary_or_position = fields.Selection(REQUEST_TYPE,
                              'Request Type', tracking=True, required=True,
                              copy=False, default='position_request')
   
    grade_id = fields.Many2one('hr.job.grade',string = "Requested Grade",domain="[('job_grade_title','=',job_title)]")

    
    @api.depends("employee_id")
    def _compute_contract(self):
         if self.employee_id:
            self.contract_id = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)], limit=1)
         else:
              self.contract_id = self.contract_id
   
    def isEmployee(self):
        #This function checks if the user applying or asking recruitment request is employee
        isemployee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        return isemployee   
    @api.model
    def create(self, vals):
        Employee = self.isEmployee()
        if not Employee:
            raise UserError(("The recruitment requester should be an employee of company ")) 

       
        vals['state'] = 'draft'
        vals['reference_no'] = self.env['ir.sequence'].next_by_code('hr.employee.position.request')
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.employee.position.request')
        request = super(HrEmployeeRequest, self).create(vals)     

        return request
    
    
    @api.depends('state')
    def send_activity_notification_to_position_Approvers(self):
        """This function will alert a for activities on job applicants"""
        
        _logger.info(" the change of state value ************************* %s  ",self.state)
            
        model = self.env['ir.model'].search([('model', '=', 'hr.employee.position.request'),('is_mail_activity','=',True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Position request mail')], limit=1)
        _logger.info("value *************************  self employee  %s activity type %s, model %s self id ,%s  and if the strings are equal waiting approval %s and the state %s and type %s",self.employee_id.user_id.id,activity_type.id,model.id,self.id,str(self.state) == "waiting_approval",self.state,type(self.state))
        if self.state == 'in_progress':
            Approvers = self.env.ref('hr_request_position.group_request_hr_approval_request').users

            for Approver in Approvers:
                message = str(Approver.name) + " , you have new Position/salary request to approve  as HR.."
                self.env['mail.activity'].sudo().create({
                    'display_name': message,
                    'summary': "Position/salary request",
                    'user_id': Approver.id,
                    'res_model_id': model.id,
                    'res_id': self.id,
                    'activity_type_id': activity_type.id
                })
                Approver.notify_warning('<h4> Your have new Position/salary request Approval in Activity.</h4>', True)
        elif self.state == 'hr_approval':
            Approvers = self.env.ref('hr_request_position.group_position_request_manager_approval').users

            for Approver in Approvers:
                message = str(Approver.name) + " , you have new Position/salary request to approve as a Manager."
                self.env['mail.activity'].sudo().create({
                    'display_name': message,
                    'summary': "Position/salary request",
                    'user_id': Approver.id,
                    'res_model_id': model.id,
                    'res_id': self.id,
                    'activity_type_id': activity_type.id
                })
                Approver.notify_warning('<h4> Your have new Position/salary request Approval in Activity.</h4>', True)
        elif self.state != 'waiting_approval' and self.state != 'draft' :
            self.env['mail.activity'].sudo().create({
                    'display_name': 'Job recruitment request status',
                    'summary': "Position/salary request",
                    'user_id': self.employee_id.user_id.id,
                    'res_model_id': model.id,
                    'res_id': self.id,
                    'activity_type_id': activity_type.id
                })
            self.employee_id.user_id.notify_warning('<h4> Position/salary request status is changed to '+str(self.state)+'.</h4>', True)

        return
    

    def button_request(self):
        if self.salary_or_position == 'position_request':
            if self.requested_position_id == self.contract_id.job_id and self.requested_department_id ==  self.department_id and self.grade_id ==  self.contract_id.grade_id:
                raise UserError(('Already in Position'))
            else:
                  self.state = 'in_progress'
                  self.send_activity_notification_to_position_Approvers()

        elif self.salary_or_position == 'salary_request':

            if(not  self.contract_id):
                  raise UserError(('Please setup the employee job contract first!'))
            
            if(not self.contract_id.wage):
                  raise UserError(('The employee current job wage is not set!'))
            
            if(not self.contract_id.grade_id):
                  raise UserError(('The job grade of the employee is not set!'))
            
            if self.estimated_salary == None:
                 raise UserError(('Estimated salary must be inserted in the input field'))
            
            if self.estimated_salary <= self.contract_id.wage:
                        raise UserError(('Please correct your estimation on provided salary to be greater than current wage of the employee.'))
            else:    
                if(self.estimated_salary < self.contract_id.grade_id.minimum_wage):
                      raise UserError(('Your estimated salary request is below your current job grade of Birr ',self.contract_id.grade_id.minimum_wage))
                
                elif (self.estimated_salary > self.contract_id.grade_id.maximum_wage):
                         raise UserError(('Your estimated salary request is above your current job grade of Birr ' ,self.contract_id.grade_id.maximum_wage))     
                else:
                      self.state = 'in_progress'
                      self.previous_salary = self.wage
                      self.send_activity_notification_to_position_Approvers()

    def write(self, vals):
        res = super(HrEmployeeRequest, self).write(vals)
        return res
        

    def hr_button_approve(self):


        if self.salary_or_position == 'salary_request':
            if self.estimated_salary <= self.contract_id.wage:
                raise UserError(('Please correct your estimation on provided salary'))
            else:
                self.write({'state':'hr_approval'})
                self.send_activity_notification_to_position_Approvers()
        
        elif self.salary_or_position == 'position_request':
            self.write({'state':'hr_approval'})
            self.send_activity_notification_to_position_Approvers()

    def manager_button_approve(self):

        if not self.contract_id:
             raise UserError(("The Requester employee doesn't have contract."))
        
        
        if self.salary_or_position == 'position_request':
            #Updating employee object and employee contract with the approved department and job postions
            self.contract_id.job_id = self.requested_position_id
            self.contract_id.department_id = self.requested_department_id.id
            self.contract_id.grade_id = self.grade_id.id
            self.contract_id.wage = self.grade_id.fixed_wage
            self.employee_id.job_id = self.requested_position_id.id
            self.employee_id.parent_id = self.requested_department_id.manager_id.id
            self.employee_id.department_id = self.requested_department_id.id
            self.employee_id.job_title = self.requested_position_id.name
            self.write({'state':'manager_approval'})
            self.send_activity_notification_to_position_Approvers()
        
        elif self.salary_or_position == 'salary_request':
            grade_id = self.env['hr.job.grade'].search([('job_dup_id', '=',self.contract_id.job_id.id),('name', '=',self.contract_id.grade_id.name)], limit=1)
            grade_id.fixed_wage = self.estimated_salary
            self.contract_id.wage = self.estimated_salary
            self.write({'state':'manager_approval'})
            self.send_activity_notification_to_position_Approvers()

    def button_reject(self):
        self.write({'state':'rejected'})
        self.send_activity_notification_to_position_Approvers()

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
  


    

class HrEmployeePrivate(models.Model):
    _inherit = "hr.employee"
    salary_request_ids = fields.One2many("hr.employee.position.request","employee_id",string="Salary Requests")
    request_count = fields.Integer(compute='_compute_equipment_count', string='Request Count')

    @api.depends('salary_request_ids')
    def _compute_equipment_count(self):
        for request in self:
            request.request_count = len(request.salary_request_ids)




