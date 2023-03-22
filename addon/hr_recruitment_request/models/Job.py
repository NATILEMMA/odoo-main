import datetime
from datetime import date
from tokenize import group
from odoo import api, fields, models
from odoo.exceptions import UserError
import os

import logging

_logger = logging.getLogger(__name__)


REQUEST_STATES = [
    ('initial_qualifications', 'Initial Qualifications'),
    ('first_interview', 'First Interview'),
    ('second_interview', 'Second Interview'),
    ('accepted','accepted'),
    ('rejected', 'Rejected'), 
]



class Job(models.Model):

  
    _name = 'custom.job'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Job Appilication'
  
    name = fields.Char(string='name', required=True,
                          readonly=True, default='New', index=True)
    
    
    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.company)
    employee_id = fields.Many2one('hr.employee',string='Applying Employee',required=True,readonly=True)
    job_title = fields.Char(string='Current Job title',related='employee_id.job_title', related_sudo=False, tracking=True,readonly=True)
    work_phone = fields.Char(string=' work phone',related='employee_id.work_phone', related_sudo=False, tracking=True,readonly=True)
    work_email = fields.Char(string='work email',related='employee_id.work_email', related_sudo=False, tracking=True,readonly=True)
    department_id = fields.Many2one(string='Current department',related='employee_id.department_id',readonly=True, related_sudo=False, tracking=True)
    work_location = fields.Char( string='Current work location',related='employee_id.work_location', related_sudo=False,readonly=True, tracking=True)
    employee_parent_id = fields.Many2one('hr.employee',string='Current Employee manager',related='employee_id.parent_id',readonly=True, related_sudo=False, tracking=True)
    contract_id = fields.Many2one('hr.contract',related='employee_id.contract_id', string='Employee Contract', help='Current contract of the employee', related_sudo=False, tracking=True)
    user_id = fields.Many2one('res.users',default = lambda self: self.env.user)
    job_poster_id = fields.Many2one('hr.employee', string="Poster entity", readonly=True)
    applied_job_department_id = fields.Many2one('hr.department' ,tracking=True,readonly=True)
    applied_job_id = fields.Many2one('hr.job',tracking=True,readonly=True)
    applied_job_title = fields.Char(string='Applied Job title', tracking=True,readonly=True)
    applied_job_department_name = fields.Char( string='Applied department',readonly=True)
    recruitment_request_id = fields.Many2one("hr.recruitment.request",required  = True)
    applied_grade_id = fields.Many2one('hr.job.grade',string = 'Applied Job grade' ,readonly=True)
    state = fields.Selection(REQUEST_STATES,
                              'Status', tracking=True,
                              copy=False, default='initial_qualifications',group_expand='_group_expand_states')
    related_position_request_id = fields.Many2one("hr.employee.position.request",readonly=True)
   

    @api.onchange('state')
    def send_Email_notification_to_job_appliers(self):
        """This function will alert a for activities on job applicants"""
        if self.employee_id:

            for record in self:
                message = str(record.employee_id.name) + "your Job application for Job"+ str(record.applied_job_id.name)+" status is "+ str(record.state)
                model = record.env['ir.model'].search([('model', '=', 'custom.job'),('is_mail_activity','=',True)])
                activity_type = record.env['mail.activity.type'].search([('name', '=', 'State change mail')], limit=1)
                _logger.info("value  record employee  %s activity type %s, model %s record id ,%s ",record.employee_id.user_id.id,activity_type.id, model.id,record._origin.id)
                self.env['mail.activity'].sudo().create({
                    'display_name': message,
                    'summary': "Status change",
                    'user_id': record.employee_id.user_id.id,
                    'res_model_id': model.id,
                    'res_id': record._origin.id,
                    'activity_type_id': activity_type.id
                })
            self.employee_id.user_id.notify_warning(message, '<h4> Your application for job '+str(self.applied_job_id.name)+ ' status is changed.</h4>', True)


    def _group_expand_states(self, state, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.model
    def create(self, vals):
        # _logger.info("this is from salary request this is contract %s",contract)
        vals['name'] = self.env['ir.sequence'].next_by_code('custom.job.sequence')
        request = super(Job, self).create(vals)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
        return request
    
    def button_accept(self):

        contract = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id)],limit =1)
        if contract:
            vals = {
                'company_id': self.company_id.id,
                'employee_id':self.employee_id.id,
                'department_id': self.department_id.id,
                'salary_or_position':'position_request',
                'state':'in_progress',
                'requested_position_id':self.applied_job_id.id,
                'requested_department_id':self.applied_job_department_id.id,
                'grade_id':self.applied_grade_id.id
            }
            result = self.env['hr.employee.position.request'].create(vals)
            _logger.info("this is the id of created positon request %s",result.id)
            self.related_position_request_id = result.id
            self.write({'state':'accepted'})
        else:
            raise UserError(("Applicant doesn't have contract.Setup a job contract to proceed"))
        
    def button_reject(self):
         self.write({'state':'rejected'})

