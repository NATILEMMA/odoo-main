"""This file will deal with the modification to be made on the members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class Stages(models.Model):
    _name="membership.stage"
    _description="This model will create different grades for members"

    name = fields.Char(required=True, string="Membership Stage", translate=True)
    color = fields.Integer()

    _sql_constraints = [
                    ('Check on name', 'UNIQUE(name)', 'Each stage must be unique')
                    ]



class EducationLevel(models.Model):
    _name="res.edlevel"
    _description="This model will contain education levels"

    name = fields.Char(required=True, translate=True)

class FieldofStudy(models.Model):
    _name="field.study"
    _description="This will craete a static fields of study"

    name = fields.Char(required=True, translate=True)

class WorkExperience(models.Model):
    _name="work.experience"
    _description="This model will create model that will hold history of work experince"

    name = fields.Char(string="Job Title", translate=True)
    place_of_work = fields.Char(string="Company Name", translate=True)
    years_of_service = fields.Char(translate=True)
    current_job = fields.Boolean(default=False)
    partner_id = fields.Many2one('res.partner', readonly=True)
   
class Transfer(models.Model):
    _name="leader.transfer"
    _description="This model will create tranfer sheets for leaders"

    partner_id = fields.Many2one('res.partner')
    leadership_experience = fields.Char(translate=True, readonly=True)
    place_of_work = fields.Char(translate=True, readonly=True)
    responsibility_in_gov = fields.Char(string="Responsibility In Goverment", translate=True, readonly=True)
    responsibility_in_org = fields.Char(string="Responsibility In Organization", translate=True, readonly=True)
    key_strength = fields.Many2many('interpersonal.skills', 'skill_leader_rel', string="Strength", readonly=True)
    key_weakness = fields.Many2many('interpersonal.skills', readonly=True)
    grade = fields.Char(translate=True, readonly=True)
    leadership_status = fields.Char(translate=True, readonly=True)
    membership_fee = fields.Float(readonly=True)

    @api.model
    def create(self, vals):
        """This will get all the transfer information from file"""
        record = super(Transfer, self).create(vals)
        record.leadership_experience = record.partner_id.experience
        record.responsibility_in_gov = record.partner_id.gov_responsibility
        record.responsibility_in_org = record.partner_id.member_responsibility
        record.key_strength = record.partner_id.key_strength.ids
        record.key_weakness = record.partner_id.key_weakness.ids
        record.grade = record.partner_id.grade
        record.leadership_status = record.partner_id.leadership_status
        work = record.partner_id.work_experience_ids.filtered(lambda rec: rec.current_job == True)
        record.place_of_work = work.place_of_work
        record.membership_fee = record.partner_id.membership_monthly_fee_cash + record.partner_id.membership_monthly_fee_cash_from_percent
        return record


class InterpersonalSkills(models.Model):
    _name="interpersonal.skills"
    _description="This model will create models that will contain a list of skills and weaknesses"

    name = fields.Char(required=True, translate=True)
    positive = fields.Boolean()

class AttachmentTypes(models.Model):
  _name="attachment.type"
  _description="This will handle the different types of attachments the member is allowed to attach"

  name = fields.Char(required=True, string="Attachment Type", translate=True)


  _sql_constraints = [
                       ('Check on name', 'UNIQUE(name)', 'Each attachment type must be unique')
                     ]

class AttachmentModification(models.Model):
  _inherit="ir.attachment"

  attachment_type = fields.Many2one('attachment.type')


class ResPartner(models.Model):
    _inherit="res.partner"

    gender = fields.Selection(selection=[('Male', 'Male'), ('Female', 'Female')], copy=False, required=True)
    age = fields.Integer(required=True)
    nation = fields.Char(translate=True)
    region = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Region")
    region_of_birth = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", string="Birth Place Region")
    zone_city_of_birth = fields.Char(translate=True, string="Zone/City of Birth")
    wereda_of_birth = fields.Char(translate=True, string="Woreda of Birth")
    education_level = fields.Many2one('res.edlevel', required=True)
    field_of_study_id = fields.Many2many('field.study')
    # education_type = fields.Selection(selection=[('formal', 'Formal'), ('informal', 'Informal'), ('non-formal', 'Non-Formal')])
    league_type = fields.Selection(selection=[('young', 'Youngsters'), ('women', 'Women')])
    league_org = fields.Selection(selection=[('labourer', 'Labourer'), ('urban dweller', 'Urban Dweller')])
    league_status = fields.Selection(selection=[('league member', 'League Member'), ('league leader', 'League Leader')], default='league member')
    other_trainings = fields.Char(translate=True)
    income = fields.Float(store=True)
    # years_of_service = fields.Char(translate=True)
    work_experience_ids = fields.One2many('work.experience', 'partner_id')
    member_complaint_ids = fields.One2many('member.complaint', 'victim_id')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    attachment_amount = fields.Integer(compute="_count_attachments")
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True)
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True, store=True)
    kebele = fields.Char(translate=True)
    start_of_membership = fields.Selection(selection=[(str(num), num) for num in range(1900, (datetime.now().year)+1 )], string='Membership Start Year')
    grade = fields.Selection(selection=[('high', 'High'), ('mid', 'Mid'), ('low', 'Low')], default='low', required=True)
    payment_method = fields.Selection(selection=[('cash', 'Cash'), ('percentage', 'Percentage')], readonly=True, store=True)
    membership_monthly_fee_cash = fields.Float(store=True)
    membership_monthly_fee_cash_from_percent = fields.Float(readonly=True, store=True)
    membership_monthly_fee_percent = fields.Float(readonly=True, store=True)
    # status = fields.Selection(selection=[('executive_committee', 'Executive Committee'), ('central_committee', 'Central Committee and Member')])
    key_strength = fields.Many2many('interpersonal.skills', 'positive_skill_rel', domain="[('positive', '=', True)]", translate=True)
    key_weakness = fields.Many2many('interpersonal.skills', domain="[('positive', '=', False)]", translate=True)
    training_center = fields.Char(translate=True)
    training_type = fields.Char(translate=True)
    training_round = fields.Integer()
    training_year = fields.Selection(selection=[(str(num), num) for num in range(1900, (datetime.now().year)+1 )], string='Training Year')
    training_result = fields.Selection(selection=[('a', 'A'), ('b', 'B'), ('c', 'C')])
    is_leader = fields.Boolean(string="Is Leader", default=False)
    membership_status = fields.Selection(selection=[('full member', 'Full Member'), ('candidate', 'Candidate')], default='candidate')
    main_office = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]")
    member_cells = fields.Many2one('member.cells', domain="[('main_office', '=', main_office)]")
    member_responsibility = fields.Char(translate=True)
    gov_responsibility = fields.Char(string="Government Responsibility", translate=True)
    demote_to_member = fields.Boolean(default=False)
    year_of_payment = fields.Many2one("fiscal.year", string='Year', store=True)
    membership_payments = fields.One2many('each.member.payment', 'member_id')
    is_leader = fields.Boolean(string="Is Leader", default=False)
    is_league = fields.Boolean(default=False)
    is_member = fields.Boolean(default=False)
    was_supporter = fields.Boolean(default=False)
    was_candidate = fields.Boolean(default=False)
    was_member = fields.Boolean(default=False)
    was_league = fields.Boolean(default=False)
    stock = fields.Selection(selection=[('selected', 'Selected'), ('not selected', 'Not Selected')], default='not selected')
    type_of_payment = fields.Selection(selection=[('in person', 'In Person'), ('bank', 'Bank')], default='in person', required=True)
    user_name = fields.Char(readonly=True)
    email_address = fields.Char()
    candidate_id = fields.Many2one('candidate.members')
    supporter_id = fields.Many2one('supporter.members')
    evaluation_main_points = fields.Text(string='Evaluation Main Points')
    decision = fields.Text(string="Decision")
    evaluated = fields.Boolean(default=False)
    leadership_status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], default='inactive')
    leader_transfer = fields.One2many('leader.transfer', 'partner_id')
    experience = fields.Char(translate=True)


    @api.model
    def create(self, vals):
        """This function will check if a record already exists"""
        exists = self.env['res.partner'].search([('name', '=', vals['name'])])
        if exists:
            raise UserError(_("A partner with the same name already exists, Please make sure it isn't a duplicated data"))
        return super(ResPartner, self).create(vals)


    def finish_evaluation(self):
        """This will make a leader evaluated and give him a badge"""
        for record in self:
            record.evaluated = True

    @api.onchange('member_cells')
    def _assign_cells_a_member(self):
        """This function will assign cells a member"""
        for record in self:
            if record.is_leader:
                remove = self.env['member.cells'].search([]).leaders_ids.ids
                if record._origin.id in remove:
                    self.env['member.cells'].search([]).leaders_ids = [(3, int(record._origin.id))]
                all_leaders = record.member_cells.leaders_ids.ids + [record._origin.id]
                record.member_cells.leaders_ids = [(5, 0, 0)]
                record.member_cells.leaders_ids = [(6, 0, all_leaders)]
            if record.is_member:
                remove = self.env['member.cells'].search([]).members_ids.ids
                if record._origin.id in remove:
                    self.env['member.cells'].search([]).members_ids = [(3, int(record._origin.id))]
                all_members = record.member_cells.members_ids.ids + [record._origin.id]
                record.member_cells.members_ids = [(5, 0, 0)]
                record.member_cells.members_ids = [(6, 0, all_members)]


    @api.onchange('year_of_payment')
    def _generate_payments(self):
        """This function will generate the payment of previous years"""
        for record in self:
            record.membership_payments = [(5, 0, 0)]
            year = self.env['fiscal.year'].search([('id', '=', record.year_of_payment.id)])
            all_payment = self.env['each.member.payment'].search([('member_id', '=', record._origin.id), ('year', '=', year.id)])
            if all_payment:
                record.write({
                    'membership_payments': [(6, 0, all_payment.ids)]
                })

    @api.onchange('demote_to_member')
    def _demote_to_member(self):
        """This function will demote a leader to a member"""
        for record in self:
            if record.demote_to_member:
                record.is_leader = False


    @api.onchange('income')
    def _compute_according_to_income(self):
        """This will compute methods of payments based on your income"""
        for record in self:
            if record.income == 0.00:
                record.payment_method = 'cash'
                record.membership_monthly_fee_cash = 0.00
            else:
                all_fee = self.env['payment.fee.configuration'].search([])
                for fee in all_fee:
                    if fee.minimum_wage <= record.income <= fee.maximum_wage:
                        record.payment_method = 'percentage'
                        record.membership_monthly_fee_percent = fee.fee_in_percent
                        record.membership_monthly_fee_cash_from_percent = (fee.fee_in_percent / 100) * record.income
                        break
                    else:
                        record.payment_method = 'percentage'
                        record.membership_monthly_fee_percent = fee.fee_in_percent
                        record.membership_monthly_fee_cash_from_percent = (fee.fee_in_percent / 100) * record.income
                        continue

    def _count_attachments(self):
        """This function will count the number of attachments"""
        for record in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
            if attachments:
                record.attachment_amount = len(attachments.mapped('type'))
            else:
                record.attachment_amount = 0



    def create_leader(self):
        """This function will create a leader from membership"""
        for record in self:
            record.is_leader = True
            record.is_member = False
            record.is_league = False
            record.state = 'approved'
            record.demote_to_member = False
            name = record.name.split()[0] + record.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                record.user_name = name
            else:
                record.user_name = name
                self.env['res.users'].create({
                    'partner_id': record.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })

    def create_league(self):
        """This function will create leagues from membership"""
        for record in self:
            record.state = 'approved'
            record.is_member = False
            record.is_leader = False
            record.is_league = True
            record.was_league = True
            name = record.name.split()[0] + record.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                record.user_name = name
            else:
                record.user_name = name
                self.env['res.users'].create({
                    'partner_id': record.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
