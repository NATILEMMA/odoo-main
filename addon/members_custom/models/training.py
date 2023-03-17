"""This file will deal with training for leaders"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class TrainingType(models.Model):
    _name="training.type"
    _description="This will create the training types"

    name = fields.Char(required=True, translate=True)

class Trainings(models.Model):
    _name="leaders.trainings"
    _description="This will handle trainings for leaders"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    training_center = fields.Many2one('res.partner')
    training_type = fields.Many2one('training.type', required=True)
    training_round = fields.Integer()
    training_year = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year', required=True)
    training_result = fields.Selection(selection=[('A', 'A'), ('B', 'B'), ('C', 'C')])
    partner_id = fields.Many2one('res.partner')
    leader_responsibility = fields.Many2one(related="partner_id.leader_responsibility")
    training_id = fields.Many2one('member.training')
    certificate = fields.Boolean(default=True, string="Certificates")

class MemberTraining(models.Model):
    _name = 'member.training'
    _description = "Member Training"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    def _default_wereda(self):
        """This will make the wereda the default wereda for the current user"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    wereda_id = fields.Many2one('membership.handlers.branch', default=_default_wereda)
    training_type = fields.Many2one('training.type', required=True)
    instution_type_id = fields.Many2one("hr.employee.instution.type", string="Instution Type")
    instution_id = fields.Many2one("res.partner", string="Instution",domain= "[('instution_type_id','=',instution_type_id)]", required=True)
    training_round = fields.Integer(required=True)
    training_year = fields.Selection(selection=[(str(num), num) for num in range(1980, (datetime.now().year)+1 )], string='Membership Start Year', required=True)
    start_date = fields.Date()
    end_date = fields.Date()
    leader_ids = fields.One2many('leaders.trainings', 'training_id')
    note_id = fields.Text('Description')
    state = fields.Selection([
        ('new', 'New'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Canceled'),
        ('complete', 'Completed'),
        ('print', 'Print'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='new')


    @api.model
    def create(self, vals):
        """This function will create a payment and save it as a draft"""
        vals['name'] = self.env['ir.sequence'].next_by_code('member.training')
        vals['state'] = 'new'
        return super(MemberTraining, self).create(vals)


    @api.onchange('training_type', 'instution_id', 'training_round', 'training_year')
    def _populate_leaders(self):
        """This function will populate leaders based on the information given"""
        for record in self:
            if record.training_type and record.instution_id and record.training_round and record.training_year:
                if record.leader_ids:
                    leader_ids = [(5, 0, 0)]
                leaders = self.env['res.partner'].search([('wereda_id', '=', record.wereda_id.id), ('is_leader', '=', True)])
                for leader in leaders:
                    trainings = self.env['leaders.trainings'].sudo().create({
                        'training_center': record.instution_id.id,
                        'training_type': record.training_type.id,
                        'training_round': record.training_round,
                        'training_year': record.training_year,
                        'partner_id': leader.id,
                        'training_id': record.id,
                    })

    def print_event(self):
        """This function will print out ceritificates"""
        for record in self:
            data = {}
            leader_info = []
            if record.leader_ids:
                for leader in record.leader_ids:
                    leader_info.append({
                        'name': leader.partner_id.name,
                        'program_name': record.training_type.name,
                        'program_round': record.training_round,
                        'program_convener': record.instution_id.name,
                        'date_from': record.start_date,
                        'date_to': record.end_date,
                        'result': leader.training_result,
                        'year': record.training_year
                    })
                data = {
                    'data': leader_info
                }
        # self.ensure_one()
        # started_date = datetime.strftime(self.create_date, "%Y-%m-%d ")
        # duration = (self.write_date - self.create_date).days
        # pause = relativedelta(hours=0)
        # difference = relativedelta(self.write_date, self.create_date) - pause
        # hours = difference.hours
        # minutes = difference.minutes
        # data = {
        #     'dept_id': self.program_department.id,
        #     'program_name': self.program_id.name,
        #     'program_round': self.program_round_id.name,
        #     'company_name': self.company_id.name,
        #     'institution':self.instution_id.name,
        #     'date_to': started_date,
        #     'duration': duration,
        #     'hours': hours,
        #     'minutes': minutes,
        #     'program_convener': self.program_convener.name,

        # }
        record.state = 'print'
        return self.env.ref('members_custom.create_training_certificate').report_action(self, data=data)

    def complete_event(self):
        """This function will change state"""
        for record in self:
            record.state = 'complete'

    def confirm_event(self):
        """This function will change state"""
        for record in self:
            record.state = 'confirm'

    def cancel_event(self):
        """This function will change state"""
        for record in self:
            record.state = 'cancel'