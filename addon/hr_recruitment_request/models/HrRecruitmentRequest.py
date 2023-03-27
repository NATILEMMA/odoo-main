import datetime
from datetime import date
from tokenize import group
from odoo import api, fields, models
from odoo.exceptions import UserError
import os

import logging

_logger = logging.getLogger(__name__)




REQUEST_STATES = [
    ('draft', 'Draft'),
    ('waiting_approval', 'Waiting Approval'),
    ('approved', 'Approved' ),
    ('in_external_recruitment', 'In External recruitment'),
    ('in_internal_recruitment', 'In Internal recruitment'),
    ('done', 'Done'),
    ('rejected','Rejected'), 
]

class HrRecruitmentRequest(models.Model):
    _name = 'hr.recruitment.request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Recruitment Request'

    """A recruitment request module.
       An employee where a requester role is give can request recruitment for his department, if he/she is the manager of the department.
       An employee with applier role  for approved recruitment request can apply on the record itself when the recruitment request is in state in internal recruitment or external recruitment."""

    
    name = fields.Char( required=True,readonly=True, default='New', index=True)
    
    department_id = fields.Many2one('hr.department',readonly=True, related_sudo=False,default = lambda self : self.env.user.employee_id.department_id)
    department_name = fields.Char(related='department_id.name',readonly=True)
    
    job_id = fields.Many2one('hr.job', String='Requested Postion',domain="[('department_id','=',department_id)]", required=True)
    job_title = fields.Char(related='job_id.name',default ='job', related_sudo=False)
    job_description = fields.Text(string="Job descripton")
    
    
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.company, required=True,readonly=True)
    
    expected_employees = fields.Integer(string ="Expected Employees",required=True,default = 1)
    applicant_ids = fields.One2many('custom.job','recruitment_request_id',string="Applicants")
    applicant_count = fields.Integer(compute='_compute_applicant_count')       
    applied_job_grade_id = fields.Many2one('hr.job.grade', domain="[('job_grade_title','=',job_title)]", required=True, string="Grade")

    state = fields.Selection(REQUEST_STATES,'Status',tracking=True,copy=False, default='draft')
    personal_application_count = fields.Integer(compute ="_compute_applicant_count")
   

    @api.depends('applicant_ids')
    def _compute_applicant_count(self):
        for request in self:
            request.applicant_count = len(request.applicant_ids)
        for record in self:
            for application in record.applicant_ids:
                if application.employee_id.user_id == self.env.uid:
                    record.personal_application_count += 1


    
    def isEmployee(self):
        #This function checks if the user applying or asking recruitment request is employee
        isemployee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return isemployee
    
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id

    applicant_count = fields.Integer(compute='_compute_applicant_count', string='Applicant count')
    requester_employee_id = fields.Many2one('hr.employee', string="Requested By", default=_get_employee_id, readonly=True)


    @api.depends('state')
    def send_activity_notification_to_recruitment_Approvers(self):
        """This function will alert a for activities on job applicants"""
        
        _logger.info(" the change of state value ************************* %s  ",self.state)
            
        model = self.env['ir.model'].search([('model', '=', 'hr.recruitment.request'),('is_mail_activity','=',True)])
        activity_type = self.env['mail.activity.type'].search([('name', '=', 'Recruitment request mail')], limit=1)
        _logger.info("value *************************  self employee  %s activity type %s, model %s self id ,%s  and if the strings are equal waiting approval %s and the state %s and type %s",self.requester_employee_id.user_id.id,activity_type.id,model.id,self.id,str(self.state) == "waiting_approval",self.state,type(self.state))
        if self.state == 'waiting_approval':
            Approvers = self.env.ref('hr_recruitment_request.group_recruitment_hr_approval').users

            for Approver in Approvers:
                message = str(Approver.name) + " , you have new recruitment request to approve."
                self.env['mail.activity'].sudo().create({
                    'display_name': message,
                    'summary': "Recruitment request",
                    'user_id': Approver.id,
                    'res_model_id': model.id,
                    'res_id': self.id,
                    'activity_type_id': activity_type.id
                })
                Approver.notify_warning(message, '<h4> Your have new recruitment request in Activity.</h4>', True)
        elif self.state != 'waiting_approval' and self.state != 'draft' :
            self.env['mail.activity'].sudo().create({
                    'display_name': 'Job recruitment request status',
                    'summary': "Recruitment request",
                    'user_id': self.requester_employee_id.user_id.id,
                    'res_model_id': model.id,
                    'res_id': self.id,
                    'activity_type_id': activity_type.id
                })
            self.requester_employee_id.user_id.notify_warning('<h4> Your recruitment reqeust for job '+str(self.job_title)+ ' status is changed to '+str(self.state)+'.</h4>', True)

        return
    

    @api.model
    def create(self, vals):

        Employee = self.isEmployee()

        if not Employee:
            raise UserError(("The recruitment requester should be an employee of company.")) 
        if not Employee.department_id.manager_id.id == Employee.id:
            raise UserError(("The requester should be a department manager in the company!")) 
        else:
            vals['state'] = 'draft'
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.recruitment.request.sequence')
        
            request = super(HrRecruitmentRequest, self).create(vals)
            return request
        
   
    def button_request(self):
        self.write({'state':'waiting_approval'})
        self.send_activity_notification_to_recruitment_Approvers()
    
    def button_approve(self):
        self.write({'state':'approved'})
        self.send_activity_notification_to_recruitment_Approvers()

    def button_reject(self):
        self.write({'state':'rejected'})
        self.send_activity_notification_to_recruitment_Approvers()

    def button_set_draft(self):
        self.write({'state':'draft'})
    
    def button_done(self):
        self.write({'state':'done'})
        self.send_activity_notification_to_recruitment_Approvers()

    def button_intialize_external_recruitment(self):
        vals = {
            'name': self.job_id.name,
            'company_id': self.company_id.id,
            'department_id': self.department_id.id,
            'no_of_recruitment': self.expected_employees,
            'user_id': self.env.uid,
            'state':'recruit'
        }
        #checking if there is already a recruitment with the same values
        
        existing_recruitment = self.env['hr.job'].search([('name','=',self.job_id.name),('company_id','=',self.requester_employee_id.company_id.id),('department_id','=',self.requester_employee_id.department_id.id)])
        
        if existing_recruitment:
            existing_recruitment.update({'no_of_recruitment': (existing_recruitment.no_of_recruitment + self.expected_employees)})
            self.write({'state':'in_external_recruitment'})
        else:
            result = self.env['hr.job'].create(vals)
            self.write({'state':'in_external_recruitment'})

    def button_intialize_internal_recruitment(self):
        message = "A new job for internal employees have been posted check if you are intersted"
        hr_employee = self.env.ref("hr.group_hr_user").users
        hr_employee.sudo().notify_warning(message, '<h4> New Job Post in recruitment request</h4>', True)
        self.write({'state':'in_internal_recruitment'})


    def button_apply(self):
        Employee = self.isEmployee()
        if not Employee:
            raise UserError(("The recruitment requester should be an employee of company ")) 

        current_user_employee_id = self.env.user.employee_id.id

        vals = {
            'employee_id':current_user_employee_id,
            'applied_job_title': self.job_id.name,
            'applied_job_department_id':self.department_id.id,
            'applied_job_department_name':self.department_name,
            'applied_grade_id':self.applied_job_grade_id.id,
            'recruitment_request_id':self.id,
            'applied_job_id':self.job_id.id
        }
       
        existing_applicant =  self.env['custom.job'].search([('employee_id','=',current_user_employee_id),('applied_job_title','=',self.job_id.name),('applied_job_department_id','=',self.department_id.id),('applied_grade_id','=',self.applied_job_grade_id.id)])
        
        if existing_applicant:
          raise UserError(("Already applied for this position!"))

        result = self.env['custom.job'].sudo().create(vals)

        
   

        


