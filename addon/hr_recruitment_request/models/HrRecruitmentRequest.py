from datetime import date
import datetime
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
    ('in_recruitment', 'In recruitment' ),
    ('done', 'Done'),
    ('rejected','Rejected'), 
]

class HrRecruitmentRequest(models.Model):
    _name = 'hr.recruitment.request'
    _description = 'recruitment request'

    reference_no = fields.Char(string='Request Document Reference', required=True,
                          readonly=True, default='New', index=True)

    job_id = fields.Many2one('hr.job', String='Requested Postion')
    
    job_title = fields.Char(related='job_id.name', related_sudo=False, tracking=True)

    

    state = fields.Selection(REQUEST_STATES,
                              'Status', tracking=True,
                              copy=False, default='draft')
   
    company_id = fields.Many2one('res.company', string=  'Company',default=lambda self: self.env.company, required=True)

    expected_employees = fields.Integer(string = "Expected Employees",required=True)
    
    department_id = fields.Many2one(related='employee_id.department_id', readonly=False, related_sudo=False, tracking=True)



    # _logger.info("this is from salary request this is contract %s",contract)
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id
    
    def _get_employee_department_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        
    
        return employee_rec.department_id
 
    
    employee_id = fields.Many2one('hr.employee', string="Requested By", default=_get_employee_id, readonly=True)

    
    
    department_id = fields.Many2one(related='employee_id.department_id', readonly=False, related_sudo=False, tracking=True)
    @api.model
    def create(self, vals):
        # _logger.info("this is from salary request this is contract %s",contract)

        vals['state'] = 'waiting_approval'
        vals['reference_no'] = self.env['ir.sequence'].next_by_code('hr.employee.position.request')
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
        existing_recruitment =  self.env['hr.job'].search([('name','=',self.job_id.name),('company_id','=',self.company_id.id),('department_id','=',self.department_id.id),('state','=','recruit')])
        
        _logger.info("existing recruitment %s",existing_recruitment)
        _logger.info("existing recruitment no of expected employee %s",existing_recruitment.no_of_recruitment)

        if existing_recruitment:
            existing_recruitment.update({'no_of_recruitment': (existing_recruitment.no_of_recruitment + self.expected_employees)})
            self.write({'state':'in_recruitment'})
        else:
            result = self.env['hr.job'].create(vals)
            self.write({'state':'in_recruitment'})


        
