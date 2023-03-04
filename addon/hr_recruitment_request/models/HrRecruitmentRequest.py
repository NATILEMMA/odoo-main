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
    _inherit = 'mail.thread'
    _description = 'recruitment request'

    
    reference_no = fields.Char(string='Request Document Reference', required=True,readonly=True, default='New', index=True)
    job_id = fields.Many2one('hr.job', String='Requested Postion')
    job_title = fields.Char(related='job_id.name',default ='job', related_sudo=False, tracking=True)
    job_description = fields.Text(string="Job descripton")
    state = fields.Selection(REQUEST_STATES,'Status', tracking=True,copy=False, default='draft')
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.company, required=True)
    expected_employees = fields.Integer(string ="Expected Employees",required=True)
    department_id = fields.Many2one('hr.department',readonly=False, related_sudo=False, tracking=True)
    department_name = fields.Char(related='department_id.name')
    applicant_ids = fields.One2many('custom.job','recruitment_request_id',string="Applicants")
    applicant_count = fields.Integer(compute='_compute_applicant_count', string='Applicant count')       
    # job_grade = fields.Many2one('hr.job.grade',string= "Job grade",default= lambda self :
    applied_job_grade_id = fields.Many2one('hr.job.grade', domain="[('job_grade_title','=',job_title)]", required=True, string="Grade")



    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id
 
    requester_employee_id = fields.Many2one('hr.employee', string="Requested By", default=_get_employee_id, readonly=True)

    @api.depends('applicant_ids')
    def _compute_applicant_count(self):
        _logger.info("total applicants %s",self.applicant_ids)
        for request in self:
            request.applicant_count = len(request.applicant_ids)
    applicant_count = fields.Integer(compute='_compute_applicant_count', string='Applicant count')

    @api.depends('applicant_ids')
    def _compute_applicant_count(self):
        _logger.info("total applicants %s",self.applicant_ids)
        for request in self:
            request.applicant_count = len(request.applicant_ids)
    applicant_count = fields.Integer(compute='_compute_applicant_count', string='Applicant count')

    
    @api.model
    def create(self, vals):
        _logger.info("this is refrence num %s", self.env['ir.sequence'].next_by_code('hr.recruitment.request.sequence'))

        vals['state'] = 'waiting_approval'
        vals['reference_no'] = self.env['ir.sequence'].next_by_code('hr.recruitment.request.sequence')
        request = super(HrRecruitmentRequest, self).create(vals) 

        return request

    def button_request(self):
        self.write({'state':'waiting_approval'})

    def button_approve(self):
        self.write({'state':'approved'})

    def button_reject(self):
        self.write({'state':'rejected'})


    def button_set_draft(self):
        self.write({'state':'draft'})


    def button_done(self):
        self.write({'state':'done'})

    
    def button_intialize_recruitment(self):
        vals = {
            'name': self.job_id.name,
            'company_id': self.company_id.id,
            'department_id': self.department_id.id,
            'no_of_recruitment': self.expected_employees,
            'user_id': self.env.uid,
            'state':'recruit'
        }
        #checking if there is already a recruitment with the same values
        
        existing_recruitment = self.env['hr.job'].search([('name','=',self.job_id.name),('company_id','=',self.employee_id.company_id.id),('department_id','=',self.employee_id.department_id.id)])
        
        _logger.info("existing recruitment %s",existing_recruitment)
        _logger.info("existing recruitment no of expected employee %s",existing_recruitment.no_of_recruitment)

        if existing_recruitment:
            existing_recruitment.update({'no_of_recruitment': (existing_recruitment.no_of_recruitment + self.expected_employees)})
            self.write({'state':'in_external_recruitment'})
        else:
            result = self.env['hr.job'].create(vals)
            self.write({'state':'in_external_recruitment'})

    def button_intialize_internal_recruitment(self):
        message = "A new job for internal employees have been posted check if you are intersted"
        hr_employee = self.env.ref("hr.group_hr_user").users
        hr_employee.notify_warning(message, '<h4> New Job Post</h4>', True)
        self.write({'state':'in_internal_recruitment'})


    def button_apply(self):
        current_user_employee_id = self.env.user.employee_id.id
    
        vals = {
            'employee_id':current_user_employee_id,
            'applied_job_title': self.job_id.name,
            'applied_job_department_id':self.department_id.id,
            'applied_job_department_name':self.department_name,
            'applied_grade_id':self.applied_job_grade_id.id,
            'recruitment_request_id': self.id,
            'applied_job_id':self.job_id.id
        }
        _logger.info("existing job id %s",self.job_id.name)
        _logger.info("self company of department id .id %s",self.department_id.id)
        #checking if there is already a recruitment with the same values
        existing_applicant =  self.env['custom.job'].search([('employee_id','=',current_user_employee_id),('applied_job_title','=',self.job_id.name),('applied_job_department_id','=',self.department_id.id),('applied_grade_id','=',self.applied_job_grade_id.id)])
        
        _logger.info("existing recruitment %s",existing_applicant)
        

        if existing_applicant:

            raise UserError(("Already applied for this position!"))
 
        else:
            result = self.env['custom.job'].sudo().create(vals)
            
 # _logger.info("this is from salary request this is contract %s",contract)