"""This file will deal with the handling of supporter members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class SupportingMembers(models.Model):
    _name="supporter.members"
    _description="This model will handle supporting members"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    image_1920 = fields.Binary("Image", store=True)
    name = fields.Char(translate=True, required=True, track_visibility='onchange')
    age = fields.Integer(copy=False, required=True)
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], required=True)
    ethnic_group = fields.Many2one('ethnic.groups')
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2many('field.study')
    work_place = fields.Char(translate=True, copy=False)
    position = fields.Char(translate=True, copy=False)
    income = fields.Float(track_visibility='onchange')
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True, track_visibility='onchange')
    house_number = fields.Char(translate=True)
    phone = fields.Char(track_visibility='onchange')
    status = fields.Selection(selection=[('local', 'Local'), ('foreign', 'Foreign')], default='local', track_visibility='onchange')
    gov_responsibility = fields.Char(string="Government Responsibility", translate=True, copy=False)
    start_of_support = fields.Selection(selection=[(str(num), num) for num in range(1900, (datetime.now().year)+1 )], string='Supporter Start Year', required=True)
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    state = fields.Selection(selection=[('new', 'New'), ('approved', 'Approved')], track_visibility='onchange')
    candidate_id = fields.Many2one('candidate.members', readonly=True)
    active = fields.Boolean(default=True, track_visibility='onchange')
    reason = fields.Text(translate=True)

    @api.model
    def create(self, vals):
        """This function will check if a record already exists"""
        exists = self.env['supporter.members'].search([('name', '=', vals['name']), ('gender', '=', vals['gender']), ('phone', '=', vals['phone'])])
        if exists:
            raise UserError(_("A supporter with the same name, gender and phone already exists, Please make sure it isn't a duplicated data"))
        res = super(SupportingMembers, self).create(vals)
        res.state = 'new'
        year = self.env['fiscal.year'].search([('state', '=', 'active')])
        if year.date_from <= datetime.date(res.create_date) <= year.date_to:
            plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved')])
            if plan_city:
                if res.gender == 'Male':
                    plan_city.registered_male += 1
                    plan_city.total_registered += 1
                if res.gender == 'Female':
                    plan_city.registered_female += 1
                    plan_city.total_registered += 1
                plan_city.accomplished = (plan_city.total_registered / plan_city.total_estimated) * 100
                if plan_city.accomplished <= 50.00:
                    plan_city.colors = 'orange'
                if 50 < plan_city.accomplished < 75:
                    plan_city.colors = 'blue'
                if plan_city.accomplished >= 75:
                    plan_city.colors = 'green'
            plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('subcity_id', '=', res.subcity_id.id)])
            if plan_subcity:
                if res.gender == 'Male':
                    plan_subcity.registered_male += 1
                    plan_subcity.total_registered += 1
                if res.gender == 'Female':
                    plan_subcity.registered_female += 1
                    plan_subcity.total_registered += 1 
                plan_subcity.accomplished = (plan_subcity.total_registered / plan_subcity.total_estimated) * 100
                if 30 <= plan_subcity.accomplished <= 50.00:
                    plan_subcities = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved')])
                    for plan in plan_subcities:
                        if plan.accomplished < 30:
                            plan.colors = 'red'
                    plan_subcity.colors = 'orange'
                if 50 < plan_subcity.accomplished < 75:
                    plan_subcity.colors = 'blue'
                if plan_subcity.accomplished >= 75:
                    plan_subcity.colors = 'green'
            plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved'), ('wereda_id', '=', res.wereda_id.id)])
            if plan_woreda:
                if res.gender == 'Male':
                    plan_woreda.registered_male += 1
                    plan_woreda.total_registered += 1
                if res.gender == 'Female':
                    plan_woreda.registered_female += 1
                    plan_woreda.total_registered += 1    
                plan_woreda.accomplished = (plan_woreda.total_registered / plan_woreda.total_estimated) * 100
                if 30 <= plan_woreda.accomplished <= 50.00:
                    plan_woredas = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'supporter'), ('state', '=', 'approved')])
                    for plan in plan_woredas:
                        if plan.accomplished < 30:
                            plan.colors = 'red'
                    plan_woreda.colors = 'orange'
                if 50 < plan_woreda.accomplished < 75:
                    plan_woreda.colors = 'blue'
                if plan_woreda.accomplished >= 75:
                    plan_woreda.colors = 'green'             
        return res

    @api.onchange('age')
    def _all_must_be_more_than_15(self):
        """This function will check if the age of the supporter is above 15"""
        for record in self:
            if record.age:
                if record.age < 15:
                    raise UserError(_("The Supporter's Age Must Be Above 15"))

    @api.onchange('phone')
    def _proper_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.phone:
                if len(record.phone) < 13:
                    raise UserError(_('Please Make Sure You Entered a 12 digit Phone Number with + At The Beginning'))
                elif record.phone[:4] != '+251':
                    raise UserError(_('Please Enter The Right Country Phone Code. eg +251.......')) 

    def archive_record(self):
        """This function will create wizard and archive a record"""
        wizard = self.env['archive.supporter.wizard'].create({
            'reason': self.reason
        })
        return {
            'name': _('Archive Members Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'archive.supporter.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }

    def un_archive_record(self):
        """This function will unarchive a record"""
        for record in self:
            record.active = True


    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if self.env.user.has_group('members_custom.member_group_manager') and record.state != 'new':
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False


    def create_candidate(self):
        """This function will create candidates from supporters"""
        for record in self:
            candidate = self.env['candidate.members'].sudo().create({
                'image_1920': record.image_1920,
                'name': record.name,
                'age': record.age,
                'gender': record.gender,
                'education_level': record.education_level.id,
                'field_of_study_id': record.field_of_study_id,
                'ethnic_group': record.ethnic_group.id,
                'subcity_id': record.subcity_id.id,
                'wereda_id': record.wereda_id.id,
                'house_number': record.house_number,
                'phone': record.phone,
                'income': record.income,
                'supporter_id': record.id
            })
            if record.work_place and record.position:
                candidate.write({
                    'work_experience_ids': [(0, 0, {
                        'name': record.position,
                        'place_of_work': record.work_place,
                        'current_job': True
                    })],
                })
            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year.date_from <= date.today() <= year.date_to:
                plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved')])
                if plan_city:
                    if record.gender == 'Male':
                        plan_city.registered_male += 1
                        plan_city.total_registered += 1
                    if record.gender == 'Female':
                        plan_city.registered_female += 1
                        plan_city.total_registered += 1
                    plan_city.accomplished = (plan_city.total_registered / plan_city.total_estimated) * 100
                    if plan_city.accomplished <= 50.00:
                        plan_city.colors = 'orange'
                    if 50 < plan_city.accomplished < 75:
                        plan_city.colors = 'blue'
                    if plan_city.accomplished >= 75:
                        plan_city.colors = 'green'
                plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved'), ('subcity_id', '=', record.subcity_id.id)])
                if plan_subcity:
                    if record.gender == 'Male':
                        plan_subcity.registered_male += 1
                        plan_subcity.total_registered += 1
                    if record.gender == 'Female':
                        plan_subcity.registered_female += 1
                        plan_subcity.total_registered += 1 
                    plan_subcity.accomplished = (plan_subcity.total_registered / plan_subcity.total_estimated) * 100
                    if 30 <= plan_subcity.accomplished <= 50.00:
                        plan_subcities = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved')])
                        for plan in plan_subcities:
                            if plan.accomplished < 30:
                                plan.colors = 'red'
                        plan_subcity.colors = 'orange'
                    if 50 < plan_subcity.accomplished < 75:
                        plan_subcity.colors = 'blue'
                    if plan_subcity.accomplished >= 75:
                        plan_subcity.colors = 'green'
                plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved'), ('wereda_id', '=', record.wereda_id.id)])
                if plan_woreda:
                    if record.gender == 'Male':
                        plan_woreda.registered_male += 1
                        plan_woreda.total_registered += 1
                    if record.gender == 'Female':
                        plan_woreda.registered_female += 1
                        plan_woreda.total_registered += 1
                    plan_woreda.accomplished = (plan_woreda.total_registered / plan_woreda.total_estimated) * 100
                    if 30 <= plan_woreda.accomplished <= 50.00:
                        plan_woredas = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved')])
                        for plan in plan_woredas:
                            if plan.accomplished < 30:
                                plan.colors = 'red'
                        plan_woreda.colors = 'orange'
                    if 50 < plan_woreda.accomplished < 75:
                        plan_woreda.colors = 'blue'
                    if plan_woreda.accomplished >= 75:
                        plan_woreda.colors = 'green'
            record.candidate_id = candidate
            record.state = 'approved'