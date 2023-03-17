"""This file will deal with the models dealing with membership"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta

class AnnualPlansWereda(models.Model):
   _name="annual.plans.wereda"
   _description="This model will handle the annual members estimation planning in wereda"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   name = fields.Char(required=True)
   type_of_member = fields.Selection(selection=[('supporter', 'Supporter'), ('candidate', 'Candidate'), ('league', 'League'), ('member', 'Member'), ('leader', 'Leader')], required=True, track_visibility='onchange')
   male = fields.Integer(track_visibility='onchange')
   female = fields.Integer(track_visibility='onchange')
   approved_date = fields.Date(readonly=True)
   fiscal_year = fields.Many2one("fiscal.year", string='Year', required=True, track_visibility='onchange')
   wereda_id = fields.Many2one('membership.handlers.branch', readonly=True)
   from_subcity_plan = fields.Many2one('annual.plans.subcity', readonly=True, store=True)
   total_estimated = fields.Integer(readonly=True, store=True)
   registered_male = fields.Integer(readonly=True, store=True)
   registered_female = fields.Integer(readonly=True, store=True)
   total_registered = fields.Integer(readonly=True, store=True)
   colors = fields.Selection(selection=[('red', 'Red'), ('orange', 'Orange'), ('blue', 'Blue'), ('green', 'Green')], default='orange')
   accomplished = fields.Float(digits=(12, 2), readonly=True, store=True)
   state = fields.Selection(selection=[('draft', 'Draft'), ('approved', 'Approved')], default='draft', track_visibility='onchange')

   @api.model
   def create(self, vals):
      """This function will make sure duplicate creation for same type in the same year doesn't exist"""
      exists = self.env['annual.plans.wereda'].search([('fiscal_year', '=', vals['fiscal_year']), ('type_of_member', '=', vals['type_of_member']), ('wereda_id', '=', vals['wereda_id'])])
      year = self.env['fiscal.year'].search([('id', '=', vals['fiscal_year'])])
      wereda = self.env['membership.handlers.branch'].search([('id', '=', vals['wereda_id'])])
      if exists:
         message = "A Plan for " + str(wereda.name) + " for the year " + str(year.name) + " and Type " + str(vals['type_of_member']) + " already exists."
         raise ValidationError(_(message))
      if vals['male'] == 0 and vals['female'] == 0:
         raise ValidationError(_("Please Enter An Estimated Number For Either Male or Female"))
      return super(AnnualPlansWereda, self).create(vals)

   @api.onchange('male', 'female')
   def _calculate_total_members_in_wereda(self):
      """This function will calculate the total members to register"""
      for record in self:
         if record.male or record.female:
            record.total_estimated = record.male + record.female
         if record.male and record.from_subcity_plan:
            subcity_estimated = sum(record.from_subcity_plan.mapped('male'))
            all_weredas_estimated = sum(self.env['annual.plans.wereda'].search([('from_subcity_plan', '=', record.from_subcity_plan.id)]).mapped('male'))
            all_weredas = record.male + all_weredas_estimated
            if all_weredas > subcity_estimated:
               raise ValidationError(_("The Sum of The Estimated Number of Members To Register in Your Woredas Has Exceeded The Total Estimated From Your Subcity"))
         if record.female and record.from_subcity_plan:
            subcity_estimated = sum(record.from_subcity_plan.mapped('female'))
            all_weredas_estimated = sum(self.env['annual.plans.wereda'].search([('from_subcity_plan', '=', record.from_subcity_plan.id)]).mapped('female'))
            all_weredas = record.female + all_weredas_estimated
            if all_weredas > subcity_estimated:
               raise ValidationError(_("The Sum of The Estimated Number of Members To Register in Your Woredas Has Exceeded The Total Estimated From Your Subcity"))

   @api.onchange('total_estimated')
   def _not_more_than_planned_subcity(self):
      """This function will make sure that the planned amount doesn't exceed the assigned amount"""
      for record in self:
         if record.from_subcity_plan:
            subcity_estimated = sum(record.from_subcity_plan.mapped('total_estimated'))
            all_weredas_estimated = sum(self.env['annual.plans.wereda'].search([('from_subcity_plan', '=', record.from_subcity_plan.id)]).mapped('total_estimated'))
            all_weredas = record.total_estimated + all_weredas_estimated
            if all_weredas > subcity_estimated:
               raise ValidationError(_("The Sum of The Estimated Number of Members To Register in Your Woredas Has Exceeded The Total Estimated From Your Subcity"))

   @api.onchange('fiscal_year')
   def _default_plan_subcity(self):
      """This function will give the default plan for subcities"""
      for record in self:
         if record.fiscal_year and record.wereda_id:
            record.from_subcity_plan = self.env['annual.plans.subcity'].search([('fiscal_year', '=', record.fiscal_year.id), ('subcity_id', '=', record.wereda_id.parent_id.id), ('state', '=', 'approved'), ('type_of_member', '=', record.type_of_member)])

   def change_state(self):
      """This function will chnage the state of the annual plan"""
      for record in self:
         record.approved_date = date.today()
         record.state = 'approved'

class AnnualPlansSubcity(models.Model):
   _name="annual.plans.subcity"
   _description="This model will handle the annual members estimation planning in subcity"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   name = fields.Char(required=True)
   type_of_member = fields.Selection(selection=[('supporter', 'Supporter'), ('candidate', 'Candidate'), ('league', 'League'), ('member', 'Member'), ('leader', 'Leader')], required=True, track_visibility='onchange')
   male = fields.Integer(track_visibility='onchange')
   female = fields.Integer(track_visibility='onchange')
   approved_date = fields.Date(readonly=True)
   fiscal_year = fields.Many2one("fiscal.year", string='Year', required=True, track_visibility='onchange')
   subcity_id = fields.Many2one('membership.handlers.parent', readonly=True)
   from_city_plan = fields.Many2one('annual.plans', readonly=True, store=True)
   total_estimated = fields.Integer(readonly=True, store=True)
   registered_male = fields.Integer(readonly=True, store=True)
   registered_female = fields.Integer(readonly=True, store=True)
   total_registered = fields.Integer(readonly=True, store=True)
   colors = fields.Selection(selection=[('red', 'Red'), ('orange', 'Orange'), ('blue', 'Blue'), ('green', 'Green')], default='orange')
   accomplished = fields.Float(digits=(12, 2), readonly=True, store=True)
   state = fields.Selection(selection=[('draft', 'Draft'), ('approved', 'Approved')], default='draft', track_visibility='onchange')

   @api.model
   def create(self, vals):
      """This function will make sure duplicate creation for same type in the same year doesn't exist"""
      exists = self.env['annual.plans.subcity'].search([('fiscal_year', '=', vals['fiscal_year']), ('type_of_member', '=', vals['type_of_member']), ('subcity_id', '=', vals['subcity_id'])])
      year = self.env['fiscal.year'].search([('id', '=', vals['fiscal_year'])])
      subcity = self.env['membership.handlers.parent'].search([('id', '=', vals['subcity_id'])])
      if exists:
         message = "A Plan for " + str(subcity.name) + " for the year " + str(year.name) + " and Type " + str(vals['type_of_member']) + " already exists."
         raise ValidationError(_(message))
      if vals['male'] == 0 and vals['female'] == 0:
         raise ValidationError(_("Please Enter An Estimated Number For Either Male or Female"))
      return super(AnnualPlansSubcity, self).create(vals)

   @api.onchange('total_estimated')
   def _not_more_than_planned_subcity(self):
      """This function will make sure that the planned amount doesn't exceed the assigned amount"""
      for record in self:
         if record.from_city_plan:
            city_estimated = sum(record.from_city_plan.mapped('total_estimated'))
            all_subcity_estimated = sum(self.env['annual.plans.subcity'].search([('from_city_plan', '=', record.from_city_plan.id)]).mapped('total_estimated'))
            all_subcity = record.total_estimated + all_subcity_estimated
            if all_subcity > city_estimated:
               raise ValidationError(_("The Sum of The Estimated Number of Members To Register in Subcities Has Exceeded The Total Estimated From City"))

   @api.onchange('male', 'female')
   def _calculate_total_members_in_subcity(self):
      """This function will calculate the total members to register"""
      for record in self:
         if record.male or record.female:
            record.total_estimated = record.male + record.female
         if record.male and record.from_city_plan:
            subcity_estimated = sum(record.from_city_plan.mapped('male'))
            all_weredas_estimated = sum(self.env['annual.plans.subcity'].search([('from_city_plan', '=', record.from_city_plan.id)]).mapped('male'))
            all_weredas = record.male + all_weredas_estimated
            if all_weredas > subcity_estimated:
               raise ValidationError(_("The Sum of The Estimated Number of Members To Register in Your Woredas Has Exceeded The Total Estimated From Your Subcity"))
         if record.female and record.from_city_plan:
            subcity_estimated = sum(record.from_city_plan.mapped('female'))
            all_weredas_estimated = sum(self.env['annual.plans.subcity'].search([('from_city_plan', '=', record.from_city_plan.id)]).mapped('female'))
            all_weredas = record.female + all_weredas_estimated
            if all_weredas > subcity_estimated:
               raise ValidationError(_("The Sum of The Estimated Number of Members To Register in Your Woredas Has Exceeded The Total Estimated From Your Subcity"))

   @api.onchange('fiscal_year')
   def _default_plan_subcity(self):
      """This function will give the default plan for subcities"""
      for record in self:
         if record.fiscal_year and record.subcity_id:
            record.from_city_plan = self.env['annual.plans'].search([('fiscal_year', '=', record.fiscal_year.id), ('city_id', '=', record.subcity_id.city_id.id), ('state', '=', 'approved'), ('type_of_member', '=', record.type_of_member)])

   def change_state(self):
      """This function will chnage the state of the annual plan"""
      for record in self:
         record.approved_date = date.today()
         record.state = 'approved'

class AnnualPlans(models.Model):
   _name="annual.plans"
   _description="This model will handle the annual members estimation planning"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   name = fields.Char(required=True)
   type_of_member = fields.Selection(selection=[('supporter', 'Supporter'), ('candidate', 'Candidate'), ('league', 'League'), ('member', 'Member'), ('leader', 'Leader')], required=True, track_visibility='onchange')
   male = fields.Integer(track_visibility='onchange')
   female = fields.Integer(track_visibility='onchange')
   approved_date = fields.Date(readonly=True)
   fiscal_year = fields.Many2one("fiscal.year", string='Year', required=True, track_visibility='onchange')
   city_id = fields.Many2one('membership.city.handlers', readonly=True)
   total_estimated = fields.Integer(readonly=True, store=True)
   registered_male = fields.Integer(readonly=True, store=True)
   registered_female = fields.Integer(readonly=True, store=True)
   total_registered = fields.Integer(readonly=True, store=True)
   colors = fields.Selection(selection=[('red', 'Red'), ('orange', 'Orange'), ('blue', 'Blue'), ('green', 'Green')], default='orange')
   accomplished = fields.Float(digits=(12, 2), readonly=True, store=True)
   state = fields.Selection(selection=[('draft', 'Draft'), ('approved', 'Approved')], default='draft', track_visibility='onchange')


   @api.model
   def create(self, vals):
      """This function will make sure duplicate creation for same type in the same year doesn't exist"""
      exists = self.env['annual.plans'].search([('fiscal_year', '=', vals['fiscal_year']), ('type_of_member', '=', vals['type_of_member']), ('city_id', '=', vals['city_id'])])
      year = self.env['fiscal.year'].search([('id', '=', vals['fiscal_year'])])
      city = self.env['membership.city.handlers'].search([('id', '=', vals['city_id'])])
      if exists:
         message = "A Plan for " + str(city.name) + " for the year " + str(year.name) + " and Type " + str(vals['type_of_member']) + " already exists."
         raise ValidationError(_(message))
      if vals['male'] == 0 and vals['female'] == 0:
         raise ValidationError(_("Please Enter An Estimated Number For Either Male or Female"))
      return super(AnnualPlans, self).create(vals)

   @api.onchange('male', 'female')
   def _calculate_total_members(self):
      """This function will calculate the total members to register"""
      for record in self:
         if record.male or record.female:
            record.total_estimated = record.male + record.female

   def change_state(self):
      """This function will chnage the state of the annual plan"""
      for record in self:
         record.approved_date = date.today()
         record.state = 'approved'

class ResponsibleBodies(models.Model):
   _name="responsible.bodies"
   _description="This model will handle with the creation of Responsible bodies"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   name = fields.Char(translate=True)
   system_admin = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_user_admin").id)], string="System Adminstrator", required=True, track_visibility='onchange')
   responsible_for_ids = fields.One2many('membership.city.handlers', 'responsible_id', copy=False, readonly=True)

class MembershipCityHandlers(models.Model):
   _name="membership.city.handlers"
   _description="City Wide Handlers"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   name = fields.Char(required=True, string="City", translate=True, copy=False)
   city_manager = fields.Many2many('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_city_admin").id)], string="City Administrator", required=True, track_visibility='onchange') 
   transfer_handler = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_city_transfer_handler").id)], string="Leaders Transfer Handlers", required=True, track_visibility='onchange')
   responsible_id = fields.Many2one('responsible.bodies', readonly=True)  
   subcity_ids = fields.One2many('membership.handlers.parent', 'city_id', copy=False, readonly=True, track_visibility='onchange')
   annual_plans_ids = fields.One2many('annual.plans', 'city_id', track_visibility='onchange')


class MembershipHandlersParent(models.Model):
   _name="membership.handlers.parent"
   _description="Subcity Handlers"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   def _default_city(self):
      """This function will add the correct city for subcities"""
      return self.env['membership.city.handlers'].search([('id', '=', 1)]).id

   name = fields.Char(required=True, string="Subcity/Sector", translate=True, copy=False, track_visibility='onchange')
   parent_manager = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_admin").id)], string="Subcity Manager", copy=False, required=True, track_visibility='onchange')
   branch_ids = fields.One2many('membership.handlers.branch', 'parent_id', copy=False, readonly=True, track_visibility='onchange')
   city_id = fields.Many2one('membership.city.handlers', default=_default_city, readonly=True)
   state = fields.Selection(selection=[('new', 'New')], default='new')
   is_special_subcity = fields.Boolean(default=False)
   annual_plans_subcity_ids = fields.One2many('annual.plans.subcity', 'subcity_id', track_visibility='onchange')

class MembershipHandlersChild(models.Model):
   _name="membership.handlers.branch"
   _description="Woreda Handlers"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   name = fields.Char(required=True, string="Woreda", translate=True, copy=False, track_visibility='onchange')
   parent_id = fields.Many2one('membership.handlers.parent', string="Subcity", copy=False, required=True, track_visibility='onchange')
   branch_manager = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("members_custom.member_group_manager").id)], string="Woreda Manager", required=True, track_visibility='onchange')
   complaint_handler = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("members_custom.member_group_complaint_management").id)], required=True, track_visibility='onchange')
   is_special_woreda = fields.Boolean(default=False)
   main_office_ids = fields.One2many('main.office', 'wereda_id', readonly=True, copy=False, track_visibility='onchange')
   annual_plans_wereda_ids = fields.One2many('annual.plans.wereda', 'wereda_id', track_visibility='onchange')

class Fake(models.Model):
   _name="leader.transfer"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   name= fields.Char()

class Transfer(models.Model):
   _name="members.transfer"
   _description="This model will create tranfer sheets for leaders"
   _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

   def _default_wereda(self):
      """This function will set a default value to wereda"""
      return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

   name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
   wereda_id = fields.Many2one('membership.handlers.branch', default=_default_wereda)
   wereda_manager_id = fields.Many2one('res.users', related="wereda_id.branch_manager", store=True)
   correct_user = fields.Boolean(default=False)
   partner_id = fields.Many2one('res.partner', domain="[('wereda_id', '=', wereda_id)]", track_visibility='onchange')
   is_league = fields.Boolean(related="partner_id.is_league", store=True)
   is_member = fields.Boolean(related="partner_id.is_member", store=True)
   is_leader = fields.Boolean(related="partner_id.is_leader", store=True)
   transfer_as_a_league_or_member = fields.Selection(selection=[('league', 'League'), ('member', 'Member')], track_visibility='onchange')
   transfer_as_a_leader_or_member = fields.Selection(selection=[('leader', 'Leader'), ('member', 'Member'), ('league', 'League')], track_visibility='onchange')
   from_subcity_id = fields.Many2one('membership.handlers.parent', store=True, readonly=True)
   from_wereda_id = fields.Many2one('membership.handlers.branch', domain="[('parent_id', '=', transfer_subcity_id)]", store=True, readonly=True)
   from_main_office = fields.Many2one('main.office', readonly=True, store=True)
   from_member_cells = fields.Many2one('member.cells', readonly=True, store=True) 
   from_league_main_office = fields.Many2one('main.office', readonly=True, store=True)
   from_league_member_cells = fields.Many2one('member.cells', readonly=True, store=True)   
   leadership_experience = fields.Char(translate=True, readonly=True, store=True)
   place_of_work = fields.Char(store=True, translate=True, readonly=True)
   responsibility_in_gov = fields.Char(related="partner_id.gov_responsibility", store=True)
   responsibility_in_org_league = fields.Selection(selection=[('league member', 'League Member'), ('league leader', 'League Leader')], readonly=True, store=True)
   responsibility_in_org_member = fields.Many2one('members.responsibility', store=True, readonly=True)
   responsibility_in_org_leader = fields.Many2one('leaders.responsibility', readonly=True, store=True)
   league_org = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban Dweller')], readonly=True, store=True)
   membership_org = fields.Many2one('membership.organization', readonly=True, store=True)
   key_strength = fields.Many2many('interpersonal.skills', 'skill_tranfer_rel', string="Strength", readonly=True, store=True)
   key_weakness = fields.Many2many('interpersonal.skills', readonly=True, store=True)
   grade = fields.Selection(related="partner_id.grade", store=True)
   leadership_status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], store=True, readonly=True)
   membership_status = fields.Char(default="Full Member", readonly=True)
   membership_fee = fields.Float(readonly=True, store=True)
   league_fee = fields.Float(readonly=True, store=True)
   transfer_responsibility_league = fields.Selection(selection=[('league member', 'League Member'), ('league leader', 'League Leader')], track_visibility='onchange')
   transfer_responsibility_member = fields.Many2one('members.responsibility', track_visibility='onchange')
   transfer_responsibility_leader = fields.Many2one('leaders.responsibility', track_visibility='onchange')
   transfer_membership_org = fields.Many2one('membership.organization', track_visibility='onchange')
   transfer_league_org = fields.Selection(selection=[('labourer', 'Labourer'), ('urban', 'Urban Dweller')], track_visibility='onchange')
   transfer_subcity_id = fields.Many2one('membership.handlers.parent', track_visibility='onchange')
   transfer_wereda_id = fields.Many2one('membership.handlers.branch', domain="[('parent_id', '=', transfer_subcity_id)]", store=True, track_visibility='onchange')
   transfer_main_office = fields.Many2one('main.office', domain="['&', ('member_main_type_id','=', transfer_membership_org), ('wereda_id', '=', transfer_wereda_id)]", track_visibility='onchange')
   transfer_member_cells = fields.Many2one('member.cells', domain="[('main_office', '=', transfer_main_office)]", track_visibility='onchange')
   transfer_league_main_office = fields.Many2one('main.office', domain="['&', ('league_main_type_id', '=', transfer_league_org), ('wereda_id', '=', transfer_wereda_id)]", track_visibility='onchange')
   transfer_league_member_cells = fields.Many2one('member.cells', domain="[('main_office_league', '=', transfer_league_main_office)]", track_visibility='onchange')
   state = fields.Selection(selection=[('draft', 'draft'), ('review', 'Review'), ('waiting for approval', 'Waiting For Approval'), ('approved', 'Approved'), ('rejected', 'Rejected')], track_visibility='onchange')
   responsibility_state = fields.Selection(selection=[('transfer', 'Transfer'), ('demote', 'Demote'), ('promote', 'Promote')], default='transfer', track_visibility='onchange')
   receiving_manager = fields.Many2one('res.users', readonly=True, store=True)
   # receiving_manager_subcity = fields.Many2one('res.users', readonly=True, store=True)
   receiving_manager_city = fields.Many2one('res.users', readonly=True, store=True)
   x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
   for_woreda = fields.Boolean(default=False)
   for_subcity = fields.Boolean(default=False)
   for_city = fields.Boolean(default=False)
   for_main = fields.Boolean(default=False)
   for_cell = fields.Boolean(default=False)



   @api.model
   def create(self, vals):
      """This function will create a new state"""
      vals['name'] = self.env['ir.sequence'].next_by_code('members.transfer')
      transfers = self.env['members.transfer'].search([('partner_id', '=', vals['partner_id']), ('state', 'in', ('draft', 'review', 'waiting for approval'))])
      if len(transfers.ids) > 0:
         raise ValidationError(_("This Person Has A Transfer That Hasn't Been Reviewed Yet. Please Wait Until To Make A Decision Has Been Made"))
      vals['state'] = 'draft'
      rec = super(Transfer, self).create(vals)
      if rec.partner_id and rec.transfer_as_a_league_or_member == 'member' and rec.is_league == True and rec.is_member == False and rec.is_leader == False:
         raise ValidationError(_('Only Those Leagues Who Are Also Full Members are allowed to transfer as Members'))
      if rec.partner_id and rec.transfer_as_a_leader_or_member == 'league' and rec.is_league == False:
         raise ValidationError(_('Only Those Leaders Who Are Also Leagues are allowed to transfer as Leagues'))
      if rec.partner_id and rec.transfer_as_a_league_or_member == 'league' and rec.is_league == False:
         raise ValidationError(_('Only Those Members Who Are Also Leagues are allowed to transfer as Leagues'))
      if (rec.is_league == True and rec.transfer_as_a_league_or_member == '') or (rec.is_member == True and rec.transfer_as_a_league_or_member == '') or (rec.is_leader == True and rec.transfer_as_a_leader_or_member == ''):
         raise ValidationError(_('What would you like to be transfered as?'))
      if rec.transfer_as_a_leader_or_member == 'leader':
         rec.receiving_manager = False
         rec.receiving_manager_city = rec.from_subcity_id.city_id.transfer_handler.id
      if rec.transfer_as_a_league_or_member == 'member' or rec.transfer_as_a_leader_or_member == 'member' or rec.transfer_as_a_league_or_member == 'league' or rec.transfer_as_a_leader_or_member == 'league':
         rec.receiving_manager_city = False
         rec.receiving_manager = rec.transfer_wereda_id.branch_manager.id
      # transfers = self.env['members.transfer'].search([('partner_id', '=', rec.partner_id.id), ('state', 'in', ['draft', 'review', 'waiting for approval'])])
      # if len(transfers.ids) > 0:
      #    raise ValidationError(_("This Person Has A Transfer That Hasn't Been Reviewed Yet. Please Wait Until To Make A Decision Has Been Made"))
      return rec

   # @api.onchange('transfer_responsibility_member')
   # def _member_responsibility_transfer(self):
   #    """This function will make fields invisible"""
   #    for record in self:
   #       if record.transfer_responsibility_member:
   #          if record.transfer_responsibility_member.id == 1:
   #             record.for_woreda = False
   #             record.for_subcity = False
   #             record.for_city = False
   #             record.for_main = True
   #             record.for_cell = True
   #          if record.transfer_responsibility_member.id == 2:
   #             record.for_woreda = False
   #             record.for_subcity = False
   #             record.for_city = False
   #             record.for_main = True
   #             record.for_cell = True
   #          if record.transfer_responsibility_member.id == 3:
   #             record.for_woreda = False
   #             record.for_subcity = False
   #             record.for_city = False
   #             record.for_main = True
   #             record.for_cell = False

   @api.onchange('transfer_responsibility_leader')
   def _leader_responsibility_transfer(self):
      """This function will handle with making fields Invisible"""
      for record in self:
         if record.transfer_responsibility_leader:
            if record.transfer_responsibility_leader.id == 1:
               record.for_woreda = True
               record.for_subcity = False
               record.for_city = False
               record.for_main = False
               record.for_cell = False
            if record.transfer_responsibility_leader.id == 2:
               record.for_woreda = False
               record.for_subcity = True
               record.for_city = False
               record.for_main = False
               record.for_cell = False
            if record.transfer_responsibility_leader.id == 3:
               record.for_woreda = False
               record.for_subcity = False
               record.for_city = True
               record.for_main = False
               record.for_cell = False

   def _compute_css(self):
      """This function will help remove edit button based on state"""
      for record in self:
         if self.env.user.has_group('members_custom.member_group_manager') and (record.state == 'approved' or record.state == 'rejected' or record.state == 'review'):
               record.x_css = '<style> .o_form_button_edit {display:None}</style>'
         else:
               record.x_css = False

   def add_attachment(self):
      """This function will add attachments"""
      for record in self:
         wizard = self.env['attachment.wizard'].create({
               'res_id': record.partner_id.id,
               'res_model': 'res.partner'
         })
         return {
               'name': _('Create Attachment Wizard'),
               'type': 'ir.actions.act_window',
               'res_model': 'attachment.wizard',
               'view_mode': 'form',
               'res_id': wizard.id,
               'target': 'new'
         }

   def review(self):
      """This button will start review"""
      for record in self:
         if record.for_city == True or record.for_subcity == True or record.for_woreda == True:
            if record.receiving_manager_city.id == self.env.user.id:
               record.correct_user = True   
            else:
               message = "The Transfer Handler for the city " + str(record.from_subcity_id.city_id.name) + " is the only person allowed to review this."
               raise ValidationError(_(message))            
         # elif (record.for_woreda == True and record.for_subcity == False and record.for_city == False) or (record.for_woreda == False and record.for_subcity == False and record.for_city == False):
         #    if record.receiving_manager.id == self.env.user.id:
         #       record.correct_user = True   
         #    else:
         #       message = "The manager for the woreda " + str(record.transfer_wereda_id.name) + " is the only person allowed to review this."
         #       raise ValidationError(_(message))
         else:
            if record.receiving_manager.id == self.env.user.id:
               record.correct_user = True
            else:
               message = "The manager for the Woreda " + str(record.transfer_wereda_id.name) + " is the only person allowed to review this."
               raise ValidationError(_(message))
         record.state = 'review'

   def waiting_for_approval(self):
      """This function will send the tranfer to the requested person"""
      for record in self:
      #    record.wereda_id = record.transfer_wereda_id.id
      #    if record.wereda_manager_id.id == self.env.user.id:
      #       record.correct_user = True
         record.state = 'waiting for approval'

   # @api.onchange('transfer_as_a_league_or_member')
   # def _not_member_no_transfer(self):
   #    """This function will not allow just leagues to transfer as members"""
   #    for record in self:
   #       if record.partner_id and record.transfer_as_a_league_or_member == 'member' and (record.is_member == False or record.is_leader == False):
   #          raise UserError(_('Only Those Leagues Who Are Also Full Members are allowed to transfer as Members'))


   def approve_transfer(self):
      """This function will approve the new partner"""
      for record in self:
         if record.is_leader:
            if record.transfer_as_a_leader_or_member == 'leader':
               if record.transfer_responsibility_leader.id == 1:
                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  user.write({
                     'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('members_custom.member_group_manager').id])]
                  })
                  message = str(user.name) + " Has Been Approved To Become The Manager For " + str(record.transfer_wereda_id.name) + ". Please Make The Right Adjustments for The Promoted and Removed Personnel."
                  model = self.env['ir.model'].search([('model', '=', 'membership.handlers.branch'), ('is_mail_activity', '=', True)])
                  activity_type = self.env['mail.activity.type'].search([('name', '=', 'Woreda Manager Transfer')], limit=1)
                  self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "Woreda Manager Transfer",
                        'date_deadline': date.today() + relativedelta(month=1),
                        'user_id': record.transfer_subcity_id.city_id.transfer_handler.id,
                        'res_model_id': model.id,
                        'res_id': record.transfer_wereda_id.id,
                        'activity_type_id': activity_type.id
                  })
                  record.transfer_subcity_id.city_id.transfer_handler.notify_warning(message, '<h4>Woreda Manager Transfer</h4>', True)

               if record.transfer_responsibility_leader.id == 2:
                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  user.write({
                     'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('members_custom.member_group_admin').id])]
                  })
                  message = str(user.name) + " Has Been Approved To Become The Manager For " + str(record.transfer_subcity_id.name) + ". Please Make The Right Adjustments for The Promoted and Removed Personnel."
                  model = self.env['ir.model'].search([('model', '=', 'membership.handlers.parent'), ('is_mail_activity', '=', True)])
                  activity_type = self.env['mail.activity.type'].search([('name', '=', 'Subcity Manager Transfer')], limit=1)
                  self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "Subcity Manager Transfer",
                        'date_deadline': date.today() + relativedelta(month=1),
                        'user_id': record.transfer_subcity_id.city_id.transfer_handler.id,
                        'res_model_id': model.id,
                        'res_id': record.transfer_subcity_id.id,
                        'activity_type_id': activity_type.id
                  })
                  record.transfer_subcity_id.city_id.transfer_handler.notify_warning(message, '<h4>Subcity Manager Transfer</h4>', True)

               if record.transfer_responsibility_leader.id == 3:
                  user = self.env['res.users'].search([('partner_id', '=', record.partner_id.id)])
                  user.write({
                     'groups_id': [(6, 0, [self.env.ref('base.group_user').id, self.env.ref('members_custom.member_group_city_admin').id])]
                  })
                  message = str(user.name) + " Has Been Approved To Become The Manager For " + str(record.from_subcity_id.city_id.name) + ". Please Make The Right Adjustments for The Promoted and Removed Personnel."
                  model = self.env['ir.model'].search([('model', '=', 'membership.city.handlers'), ('is_mail_activity', '=', True)])
                  activity_type = self.env['mail.activity.type'].search([('name', '=', 'City Manager Transfer')], limit=1)
                  self.env['mail.activity'].sudo().create({
                        'display_name': message,
                        'summary': "City Manager Transfer",
                        'date_deadline': date.today() + relativedelta(month=1),
                        'user_id': from_subcity_id.city_id.transfer_handler.id,
                        'res_model_id': model.id,
                        'res_id': record.from_subcity_id.city_id.id,
                        'activity_type_id': activity_type.id
                  })
                  from_subcity_id.city_id.transfer_handler.notify_warning(message, '<h4>City Manager Transfer</h4>', True)
               record.partner_id.leader_responsibility = record.transfer_responsibility_leader.id

            if record.transfer_as_a_leader_or_member == 'member':
               record.partner_id.write({
                  'subcity_id': record.transfer_subcity_id.id,
                  'wereda_id': record.transfer_wereda_id.id,
                  'main_office': record.transfer_main_office.id,
                  'member_cells': record.transfer_member_cells.id
               }) 
               record.partner_id.membership_org = record.transfer_membership_org.id
               record.from_main_office.total_members -= 1
               record.from_main_office.total_membership_fee -= record.membership_fee
               record.from_member_cells.members_ids = [(3, int(record.partner_id.id))] 
               record.transfer_main_office.total_members += 1
               record.transfer_main_office.total_membership_fee += record.membership_fee
               all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
               record.transfer_member_cells.members_ids = [(5, 0, 0)]
               record.transfer_member_cells.members_ids = [(6, 0, all_members)]

            if record.transfer_as_a_leader_or_member == 'league':
               record.partner_id.write({
                  'subcity_id': record.transfer_subcity_id.id,
                  'wereda_id': record.transfer_wereda_id.id,
                  'league_main_office': record.transfer_league_main_office.id,
                  'league_member_cells': record.transfer_league_member_cells.id
               })
               record.partner_id.league_org = record.transfer_league_org
               record.partner_id.league_status = record.transfer_responsibility_league
               record.from_league_main_office.total_leagues -= 1
               record.from_league_main_office.total_leagues_fee -= record.league_fee
               record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
               record.transfer_league_main_office.total_leagues += 1
               record.transfer_league_main_office.total_leagues_fee += record.league_fee
               all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
               record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
               record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]               

               # if record.responsibility_in_org_league == 'league leader':
               #    record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
               # if record.responsibility_in_org_league == 'league member':
               #    record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
               # record.transfer_league_main_office.total_leagues += 1
               # record.transfer_league_main_office.total_leagues_fee += record.league_fee
               # if record.transfer_responsibility_league == ' league leader':
               #    all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
               #    record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
               #    record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]
               # if record.transfer_responsibility_league == ' league member':
               #    all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
               #    record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
               #    record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]               
         else:            

            if record.transfer_as_a_league_or_member == 'league':
               record.partner_id.write({
                  'subcity_id': record.transfer_subcity_id.id,
                  'wereda_id': record.transfer_wereda_id.id,                  
                  'league_main_office': record.transfer_league_main_office.id,
                  'league_member_cells': record.transfer_league_member_cells.id
               })
               record.partner_id.league_org = record.transfer_league_org
               record.partner_id.league_status = record.transfer_responsibility_league
               record.from_league_main_office.total_leagues -= 1
               record.from_league_main_office.total_leagues_fee -= record.league_fee
               record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
               record.transfer_league_main_office.total_leagues += 1
               record.transfer_league_main_office.total_leagues_fee += record.league_fee
               all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
               record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
               record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)] 

               # if record.responsibility_in_org_league == 'league leader':
               #    record.from_league_member_cells.league_leaders_ids = [(3, int(record.partner_id.id))]
               # if record.responsibility_in_org_league == 'league member':
               #    record.from_league_member_cells.leagues_ids = [(3, int(record.partner_id.id))]
               # record.transfer_league_main_office.total_leagues += 1
               # record.transfer_league_main_office.total_leagues_fee += record.league_fee
               # if record.transfer_responsibility_league == ' league leader':
               #    print(record.transfer_league_member_cells.league_leaders_ids.ids)
               #    all_leagues = record.transfer_league_member_cells.league_leaders_ids.ids + [record.partner_id.id]
               #    print(all_leagues)
               #    record.transfer_league_member_cells.league_leaders_ids = [(5, 0, 0)]
               #    record.transfer_league_member_cells.league_leaders_ids = [(6, 0, all_leagues)]
               #    print(record.transfer_league_member_cells.league_leaders_ids.ids)
               # if record.transfer_responsibility_league == ' league member':
               #    all_leagues = record.transfer_league_member_cells.leagues_ids.ids + [record.partner_id.id]
               #    record.transfer_league_member_cells.leagues_ids = [(5, 0, 0)]
               #    record.transfer_league_member_cells.leagues_ids = [(6, 0, all_leagues)]                  


            if record.transfer_as_a_league_or_member == 'member':
               record.partner_id.write({
                  'subcity_id': record.transfer_subcity_id.id,
                  'wereda_id': record.transfer_wereda_id.id,                  
                  'main_office': record.transfer_main_office.id,
                  'member_cells': record.transfer_member_cells.id
               })
               record.partner_id.membership_org = record.transfer_membership_org.id
               record.partner_id.member_responsibility = record.transfer_responsibility_member.id
               record.from_main_office.total_members -= 1
               record.from_main_office.total_membership_fee -= record.membership_fee
               record.from_member_cells.members_ids = [(3, int(record.partner_id.id))] 
               record.transfer_main_office.total_members += 1
               record.transfer_main_office.total_membership_fee += record.membership_fee
               all_members = record.transfer_member_cells.members_ids.ids + [record.partner_id.id]
               record.transfer_member_cells.members_ids = [(5, 0, 0)]
               record.transfer_member_cells.members_ids = [(6, 0, all_members)]  

         record.state = 'approved'


   def reject_transfer(self):
      """This function will reject the new partner"""
      for record in self:
         record.wereda_id = record.from_wereda_id.id
         record.state = 'rejected'
         

   @api.onchange('partner_id', 'transfer_as_a_league_or_member', 'transfer_as_a_leader_or_member')
   def _populate_the_missing_fields(self):
      """This function will populate the missing fields from res partner"""
      for record in self:
         if record.partner_id:
            current_job = record.partner_id.work_experience_ids.filtered(lambda rec: rec.current_job == True)
            if current_job:
               record.place_of_work = current_job.place_of_work
            else:
               record.place_of_work = ''
            record.key_strength = record.partner_id.key_strength.ids
            record.key_weakness = record.partner_id.key_weakness.ids
            record.from_subcity_id = record.partner_id.subcity_id.id
            record.from_wereda_id = record.partner_id.wereda_id.id
            if record.partner_id.is_league == True:
               record.league_org = record.partner_id.league_org
               record.responsibility_in_org_league = record.partner_id.league_status
               record.league_fee = record.partner_id.league_payment 
               record.from_league_main_office = record.partner_id.league_main_office.id
               record.from_league_member_cells = record.partner_id.league_member_cells.id

            if record.partner_id.is_leader == True:
               record.leadership_experience = record.partner_id.experience
               record.responsibility_in_org_leader = record.partner_id.leader_responsibility.id
               record.membership_fee = record.partner_id.membership_monthly_fee_cash + record.partner_id.membership_monthly_fee_cash_from_percent
               record.leadership_status = record.partner_id.leadership_status
               record.membership_org = record.partner_id.membership_org.id
               record.from_main_office = record.partner_id.main_office.id
               record.from_member_cells = record.partner_id.member_cells.id

            if record.partner_id.is_member == True:
               record.membership_org = record.partner_id.membership_org.id
               record.responsibility_in_org_member = record.partner_id.member_responsibility.id
               record.membership_fee = record.partner_id.membership_monthly_fee_cash + record.partner_id.membership_monthly_fee_cash_from_percent
               record.from_main_office = record.partner_id.main_office.id
               record.from_member_cells = record.partner_id.member_cells.id