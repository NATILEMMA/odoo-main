# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Anusha @cybrosys(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.http import request





class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    certificates = fields.Boolean(default=True, string="Certificates")
    program_id = fields.Many2one('employee.training')


class EmployeeTraining(models.Model):
    _name = 'employee.training'
    _description = "Employee Training"
    _inherit = 'mail.thread'
    name = fields.Char( required=True,readonly=True, default='New', index=True)
    program_id = fields.Many2one('employee.training.program',string='Training Program', required=True)
    program_round_id = fields.Many2one('employee.training.program.round',required=True)
    program_department = fields.Many2one('hr.department', string='Department', required=True)
    program_convener = fields.Many2one('res.users', string='Responsible User', size=32, required=True)
    training_id = fields.One2many('hr.employee','program_id', string='Employee Details')
    note_id = fields.Text('Description')
    date_from = fields.Datetime(string="Date From")
    date_to = fields.Datetime(string="Date To")
    user_id = fields.Many2one('res.users', string='users', default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    instution_type_id = fields.Many2one("hr.employee.instution.type", string="Instution Type")
    instution_id = fields.Many2one("res.partner", string="Instution",domain= "[('instution_type_id','=',instution_type_id)]")

    @api.onchange('program_id')
    def onchange_round_id(self):
        for rec in self:
            program_name = rec.program_id.name
            print(program_name)
            if program_name:
                round_ids = self.env['employee.training.program'].search_read([('name','=',program_name)],limit=1)[0]['training_round_ids']
                print(round_ids)
                return {'domain': {'program_round_id': [('id', 'in',round_ids)]}}

    state = fields.Selection([
        ('new', 'New'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceled'),
        ('complete', 'Completed'),
        ('print', 'Print'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='new')

    @api.onchange('program_department')
    def employee_details(self):
        
        for rec in self:
            if rec.program_department:
                datas = self.env['hr.employee'].search([('department_id', '=', self.program_department.id)])
                self.training_id = datas

    
    @api.model
    def create(self, vals):

        vals['name'] = self.env['ir.sequence'].next_by_code('employee.training.sequence')
    
        request = super(EmployeeTraining, self).create(vals)
        return request

    def print_event(self):
        self.ensure_one()
        started_date = datetime.strftime(self.create_date, "%Y-%m-%d ")
        duration = (self.write_date - self.create_date).days
        pause = relativedelta(hours=0)
        difference = relativedelta(self.write_date, self.create_date) - pause
        hours = difference.hours
        minutes = difference.minutes
        data = {
            'dept_id': self.program_department.id,
            'program_name': self.program_id.name,
            'program_round': self.program_round_id.name,
            'company_name': self.company_id.name,
            'institution':self.instution_id.name,
            'date_to': started_date,
            'duration': duration,
            'hours': hours,
            'minutes': minutes,
            'program_convener': self.program_convener.name,

        }
        return self.env.ref('employee_orientation.print_pack_certificates').report_action(self, data=data)

    def complete_event(self):
        self.write({'state': 'complete'})

    def confirm_event(self):
        self.write({'state': 'confirm'})

    def cancel_event(self):
        self.write({'state': 'cancel'})

    def confirm_send_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('employee_orientation', 'orientation_training_mailer')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'employee.training',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })

        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

