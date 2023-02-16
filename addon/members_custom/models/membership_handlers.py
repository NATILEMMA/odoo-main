"""This file will deal with the models dealing with membership"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ResponsibleBodies(models.Model):
   _name="responsible.bodies"
   _description="This model will handle with the creation of Responsible bodies"

   name = fields.Char(translate=True)
   system_admin = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_user_admin").id)], string="System Adminstrator")
   responsible_for_ids = fields.One2many('membership.city.handlers', 'responsible_id', copy=False, readonly=True)

class MembershipCityHandlers(models.Model):
   _name="membership.city.handlers"
   _description="This model will handle city wide membership"

   name = fields.Char(required=True, string="City", translate=True, copy=False)
   city_manager = fields.Many2many('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_city_admin").id)], string="City Administrator") 
   responsible_id = fields.Many2one('responsible.bodies', readonly=True)  
   subcity_ids = fields.One2many('membership.handlers.parent', 'city_id', copy=False, readonly=True)

class MembershipHandlersParent(models.Model):
   _name="membership.handlers.parent"
   _description="This model will handle head divisions that will have child divisions"

   name = fields.Char(required=True, string="Subcity", translate=True, copy=False)
   parent_manager = fields.Many2one('res.users', domain=lambda self: [("groups_id", "=", self.env.ref("members_custom.member_group_admin").id)], string="Subcity Manager", copy=False)
   branch_ids = fields.One2many('membership.handlers.branch', 'parent_id', copy=False, readonly=True)
   city_id = fields.Many2one('membership.city.handlers', readonly=True)
   state = fields.Selection(selection=[('new', 'New')], default='new')


class MembershipHandlersChild(models.Model):
   _name="membership.handlers.branch"
   _description="This model will handle child divisions"

   name = fields.Char(required=True, string="Woreda", translate=True, copy=False)
   parent_id = fields.Many2one('membership.handlers.parent', string="Subcity", copy=False)
   branch_manager = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("members_custom.member_group_manager").id)], string="Woreda Manager")
   complaint_handler = fields.Many2one('res.users', domain=lambda self: [("groups_id","=",self.env.ref("members_custom.member_group_complaint_management").id)])
   main_office_ids = fields.One2many('main.office', 'wereda_id', readonly=True, copy=False)