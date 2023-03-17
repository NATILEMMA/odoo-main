"""This file will deal with the candidate members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ethiopian_date import EthiopianDateConverter

class CandidateMembers(models.Model):
    _name="candidate.members"
    _description="Candidate Approval"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    image_1920 = fields.Binary("Image", store=True)
    name = fields.Char(required=True, translate=True, track_visibility='onchange')
    age = fields.Integer(required=True)
    date = fields.Date(index=True)
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')], copy=False, required=True)
    ethnic_group = fields.Many2one('ethnic.groups')
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2many('field.study')
    other_job_trainings = fields.Char(translate=True)
    source_of_livelihood = fields.Selection(selection=[('governmental', 'Governmental'), ('private', 'Private'), ('individual', 'Individual'), ('stay at home', 'Stay At Home')])
    income = fields.Float(store=True)
    work_experience_ids = fields.One2many('work.experience', 'candidate_id')
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True, track_visibility='onchange')
    house_number = fields.Char()
    house_phone_number = fields.Char()
    office_phone_number = fields.Char()
    phone = fields.Char(track_visibility='onchange')
    previous_membership = fields.Boolean(default=False, string="Previous Political Membership")
    partner_id = fields.Many2one('res.partner', readonly=True)
    state = fields.Selection(selection=[('new', 'New'), ('waiting for approval', 'Waiting For Approval'), ('postponed', 'Postponed'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='new', required=True, track_visibility='onchange')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    becomes_member_on = fields.Date(string="Becomes Member On", track_visibility='onchange')
    active = fields.Boolean(default=True, track_visibility='onchange')
    reason = fields.Text(translate=True)
    supporter_id = fields.Many2one('supporter.members', store=True, readonly=True)

    @api.model
    def create(self, vals):
        """This function will compute the becomes_member_on"""
        res = super(CandidateMembers, self).create(vals)
        res.becomes_member_on = res.create_date + relativedelta(months=6)
        year = self.env['fiscal.year'].search([('state', '=', 'active')])
        if year.date_from <= datetime.date(res.create_date) <= year.date_to:
            plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved')])
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
            plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved'), ('subcity_id', '=', res.subcity_id.id)])
            if plan_subcity:
                if res.gender == 'Male':
                    plan_subcity.registered_male += 1
                    plan_subcity.total_registered += 1
                if res.gender == 'Female':
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
            plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'candidate'), ('state', '=', 'approved'), ('wereda_id', '=', res.wereda_id.id)])
            if plan_woreda:
                if res.gender == 'Male':
                    plan_woreda.registered_male += 1
                    plan_woreda.total_registered += 1
                if res.gender == 'Female':
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
        return res


    def send_notification_to_woreda_manager(self):
        """This function will alert a woreda manager for candidate approval"""
        all_candidate = self.env['candidate.members'].search([('becomes_member_on', '=', date.today()), ('state', 'in', ['new', 'postponed'])])
        for candidate in all_candidate:
            wereda_manager = candidate.wereda_id.branch_manager
            candidate.write({'state': 'waiting for approval'})
            message = str(candidate.name) + "'s 6 month is Today. Please make a decision about the state of their membership."
            model = self.env['ir.model'].search([('model', '=', 'candidate.members'), ('is_mail_activity', '=', True)])
            activity_type = self.env['mail.activity.type'].search([('name', '=', 'Candidate Approval')], limit=1)
            activity = self.env['mail.activity'].sudo().create({
                'display_name': message,
                'summary': "Approval",
                'date_deadline': date.today() + relativedelta(month=2),
                'user_id': wereda_manager.id,
                'res_model_id': model.id,
                'res_id': candidate.id,
                'activity_type_id': activity_type.id
            })
            # candidate.message_post(body=message)
            wereda_manager.notify_warning(message, '<h4>Candidate Approval</h4>', True)

    def archive_record(self):
        """This function will create wizard and archive a record"""
        wizard = self.env['archive.candidate.wizard'].create({
            'reason': self.reason
        })
        return {
            'name': _('Archive Members Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'archive.candidate.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }

    def un_archive_record(self):
        """This function will unarchive a record"""
        for record in self:
            record.active = True

    # @api.onchange('date')
    # def _calculate_age(self):
    #     """This function will calculate age from date of birth"""
    #     for record in self:
    #         # today = date.today()
    #         # if today.month < record.date.month:
    #         #     record.age = (today.year - record.date.year) - 1
    #         # else:
    #         #     record.age = today.year - record.date.year

    def postpone_approval(self):
        """This function will postpone decision"""
        for record in self:
            record.state = 'postponed'

    @api.onchange('source_of_livelihood')
    def _remove_data(self):
       """This function will remove data if source_of_livelihood is stay at home"""
       for record in self:
           if record.source_of_livelihood == 'stay at home':
               for jobs in record.work_experience_ids:
                   jobs.current_job = False

    @api.onchange('phone')
    def _proper_phone_number(self):
        """This function will check if phone is of proper format"""
        for record in self:
            if record.phone:
                if len(record.phone) < 13:
                    raise UserError(_('Please Make Sure You Entered a 12 digit Phone Number with + At The Beginning'))
                elif record.phone[:4] != '+251':
                    raise UserError(_('Please Enter The Right Country Phone Code. eg +251.......'))


    @api.onchange('house_phone_number')
    def _proper_house_phone_number(self):
        """This function will check if house_phone_number is of proper format"""
        for record in self:
            if record.house_phone_number:
                if len(record.house_phone_number) < 13:
                    raise UserError(_('Please Make Sure You Entered a 12 digit Phone Number with + At The Beginning'))
                elif record.house_phone_number[:4] != '+251':
                    raise UserError(_('Please Enter The Right Country Phone Code. eg +251.......'))

    @api.onchange('office_phone_number')
    def _proper_office_phone_number(self):
        """This function will check if house_phone_number is of proper format"""
        for record in self:
            if record.office_phone_number:
                if len(record.office_phone_number) < 13:
                    raise UserError(_('Please Make Sure You Entered a 12 digit Phone Number with + At The Beginning'))
                elif record.office_phone_number[:4] != '+251':
                    raise UserError(_('Please Enter The Right Country Phone Code. eg +251.......'))

    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if (record.state == 'approved' or record.state == 'rejected'):
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False


    def create_members(self):
        """This function will create members from candidates"""
        for record in self:
            if record.age < 18:
                raise UserError(_("A Candidate Who Is Not 18 Or Above Can't Be A Member"))
            partner = self.env['res.partner'].sudo().create({
                'image_1920': record.image_1920,
                'name': record.name,
                'gender': record.gender,
                'age': record.age,
                'ethnic_group': record.ethnic_group.id,
                'education_level': record.education_level.id,
                'field_of_study_id': record.field_of_study_id,
                'income': record.income,
                'subcity_id': record.subcity_id.id,
                'wereda_id': record.wereda_id.id,
                'phone': record.phone,
                'house_number': record.house_number,
                'was_candidate': True,
                'was_supporter': True,
                'was_member': True,
                'is_member': True,
                'is_leader': False,
                'is_league': False,
                'candidate_id': record.id,
                'supporter_id': record.supporter_id.id
            })
            for experience in record.work_experience_ids:
                partner.write({
                    'work_experience_ids': [(0, 0, {
                        'name': experience.name,
                        'place_of_work': experience.place_of_work,
                        'years_of_service': experience.years_of_service,
                        'current_job': experience.current_job
                    })],
                })
            if record.income == 0.00:
                partner.write({
                    'payment_method': 'cash',
                    'membership_monthly_fee_percent': 0.00,
                    'membership_monthly_fee_cash': 0.00
                })
            else:
                all_fee = self.env['payment.fee.configuration'].search([])
                for fee in all_fee:
                    if fee.minimum_wage <= record.income <= fee.maximum_wage:
                        partner.write({
                            'payment_method': 'percentage',
                            'membership_monthly_fee_percent': fee.fee_in_percent,
                            'membership_monthly_fee_cash_from_percent': (fee.fee_in_percent / 100) * record.income,
                        })
                        break
                    else:
                        partner.write({
                            'payment_method': 'percentage',
                            'membership_monthly_fee_percent': fee.fee_in_percent,
                            'membership_monthly_fee_cash_from_percent': (fee.fee_in_percent / 100) * record.income,
                        })
                        continue
            if partner.phone:
                name = partner.name.split()[0] + partner.phone[-4:]
                existing = self.env['res.users'].sudo().search([('login', '=', name)])
                if existing:
                    name = partner.name.split()[0] + partner.phone[-9:]
                    partner.user_name = name
                    partner.has_user_name = True
                    self.env['res.users'].create({
                        'partner_id': partner.id,
                        'login': name,
                        'password': '123456',
                        'groups_id': [self.env.ref('base.group_portal').id],
                    })
                else:
                    partner.user_name = name
                    partner.has_user_name = True
                    self.env['res.users'].create({
                        'partner_id': partner.id,
                        'login': name,
                        'password': '123456',
                        'groups_id': [self.env.ref('base.group_portal').id],
                    })
            record.state = 'approved'
            record.partner_id = partner.id

            year = self.env['fiscal.year'].search([('state', '=', 'active')])
            if year.date_from <= date.today() <= year.date_to:
                plan_city = self.env['annual.plans'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved')])
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
                plan_subcity = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved'), ('subcity_id', '=', record.subcity_id.id)])
                if plan_subcity:
                    if record.gender == 'Male':
                        plan_subcity.registered_male += 1
                        plan_subcity.total_registered += 1
                    if record.gender == 'Female':
                        plan_subcity.registered_female += 1
                        plan_subcity.total_registered += 1 
                    plan_subcity.accomplished = (plan_subcity.total_registered / plan_subcity.total_estimated) * 100
                    if 30 <= plan_subcity.accomplished <= 50.00:
                        plan_subcities = self.env['annual.plans.subcity'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved')])
                        for plan in plan_subcities:
                            if plan.accomplished < 30:
                                plan.colors = 'red'
                        plan_subcity.colors = 'orange'
                    if 50 < plan_subcity.accomplished < 75:
                        plan_subcity.colors = 'blue'
                    if plan_subcity.accomplished >= 75:
                        plan_subcity.colors = 'green'
                plan_woreda = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved'), ('wereda_id', '=', record.wereda_id.id)])
                if plan_woreda:
                    if record.gender == 'Male':
                        plan_woreda.registered_male += 1
                        plan_woreda.total_registered += 1
                    if record.gender == 'Female':
                        plan_woreda.registered_female += 1
                        plan_woreda.total_registered += 1
                    plan_woreda.accomplished = (plan_woreda.total_registered / plan_woreda.total_estimated) * 100
                    if 30 <= plan_woreda.accomplished <= 50.00:
                        plan_woredas = self.env['annual.plans.wereda'].search([('fiscal_year', '=', year.id), ('type_of_member', '=', 'member'), ('state', '=', 'approved')])
                        for plan in plan_woredas:
                            if plan.accomplished < 30:
                                plan.colors = 'red'
                        plan_woreda.colors = 'orange'
                    if 50 < plan_woreda.accomplished < 75:
                        plan_woreda.colors = 'blue'
                    if plan_woreda.accomplished >= 75:
                        plan_woreda.colors = 'green'
            wizard = self.env['create.from.candidate.wizard'].create({
                'partner_id': partner.id
            })
            return {
                'name': _('Create Members From Candidate Wizard'),
                'type': 'ir.actions.act_window',
                'res_model': 'create.from.candidate.wizard',
                'view_mode': 'form',
                'res_id': wizard.id,
                'target': 'new'
            }