"""This file will deal with the modification to be made on offices"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta


class MainOffice(models.Model):
    _name="main.office"
    _description="This model will contain the main offices the cells bellong in"

    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).parent_id.id

    name = fields.Char(required=True, translate=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, copy=False, default=_default_subcity, domain="[('branch_ids.branch_manager', '=', user_id)]")
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda, domain="[('parent_id', '=', subcity_id)]")
    main_type_id = fields.Char(translate=True)
    cell_ids = fields.One2many('member.cells', 'main_office', readonly=True, copy=False)
    total_cell = fields.Integer(compute="_calculate_cells")
    total_members = fields.Integer(compute="_calculate_cells")
    leader_ids = fields.Many2many('res.partner', copy=False)
    total_membership_fee = fields.Float(compute="_calculate_cells")
    date_of_meeting_eachother = fields.Date()
    place_of_meeting_eachother = fields.Char(translate=True)
    time_of_meeting_eachother = fields.Float()
    date_of_meeting_cells = fields.Date()
    place_of_meeting_cells = fields.Char(translate=True)
    time_of_meeting_cells = fields.Float()
    meeting_memebers_every = fields.Integer()

    @api.depends('cell_ids')
    def _calculate_cells(self):
        """This function will calculate the total cells of main_office"""
        for record in self:
            record.total_cell = len(record.cell_ids.ids)
            total = record.cell_ids.mapped('total')
            count = 0
            for memb in total:
                count += memb
            record.total_members = count            
            total_memb_fee = record.cell_ids.mapped('total_membership_fee')
            total_membership_fee = 0
            for i in total_memb_fee:
                total_membership_fee += i
            record.total_membership_fee = total_membership_fee
            record.leader_ids = record.cell_ids.mapped('leaders_ids').ids


class Cells(models.Model):
    _name="member.cells"
    _description="This model will contain the cells members will belong in"


    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).parent_id.id

    name = fields.Char(required=True, translate=True)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, copy=False, default=_default_subcity, domain="[('branch_ids.branch_manager', '=', user_id)]")
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda, domain="[('parent_id', '=', subcity_id)]")
    main_office = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]", required=True)
    cell_type_id = fields.Char(translate=True)
    members_ids = fields.Many2many('res.partner', domain="['&', '&', ('wereda_id', '=', wereda_id), ('is_leader', '=', False), ('member_cells', '=', False), ('is_league', '=', False)]")
    date_of_meeting = fields.Date()
    place_of_meeting = fields.Char(translate=True)
    time_of_meeting = fields.Float()
    total = fields.Integer(store=True)
    leaders_ids = fields.Many2many('res.partner', 'leader_cell_rel', domain="['&', '&', ('is_leader', '=', True), ('wereda_id', '=', wereda_id), ('member_cells', '=', False), ('is_league', '=', False)]", string="Leaders")
    leagues_ids = fields.Many2many('res.partner', 'league_cell_rel', domain="['&', '&', ('is_league', '=', True), ('wereda_id', '=', wereda_id), ('member_cells', '=', False), ('is_leader', '=', False)]", string="Leagues")
    all_partners = fields.Many2many('res.partner', 'all_partner_rel', store=True)
    total_members = fields.Integer(compute="_calculate_total_members", store=True)
    total_leaders = fields.Integer(compute="_assign_leaders_cells", store=True)
    total_leagues = fields.Integer(compute="_calculate_total_leagues", store=True)
    total_leader_fee = fields.Float(store=True)
    total_member_fee = fields.Float(store=True)
    total_league_fee = fields.Float(store=True)
    total_membership_fee = fields.Float(compute="_compute_totals", store=True)
    total = fields.Integer(compute="_all_members", store=True)


    @api.depends('leaders_ids')
    def _assign_leaders_cells(self):
        """This function will assign leaders their respective main office and cells"""
        for record in self:
            total = 0.00
            record.total_leaders = len(record.leaders_ids.ids)
            if record.leaders_ids:
                for leader in record.leaders_ids:
                    leader.write({
                        'main_office': record.main_office.id,
                        'member_cells': record.id
                    })
                    total += (leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent)
            record.total_leader_fee = total

    @api.depends('members_ids')
    def _calculate_total_members(self):
        """This function will calculate the total members"""
        for record in self:
            total = 0.00
            record.total_members = len(record.members_ids.ids)
            if record.members_ids:
                for memb in record.members_ids:
                    memb.write({
                        'main_office': record.main_office.id,
                        'member_cells': record.id
                    })
                    total += (memb.membership_monthly_fee_cash + memb.membership_monthly_fee_cash_from_percent)
            record.total_member_fee = total

    @api.depends('leagues_ids')
    def _calculate_total_leagues(self):
        """This function will calculate the total leagues"""
        for record in self:
            total = 0.00
            record.total_leagues = len(record.leagues_ids.ids)
            if record.leagues_ids:
                for league in record.leagues_ids:
                    league.write({
                        'main_office': record.main_office.id,
                        'member_cells': record.id
                    })
                    total += (league.league_payment)
            record.total_league_fee = total        


    @api.depends('total_members', 'total_leaders', 'total_leagues')
    def _all_members(self):
        """Collect all in one"""
        for record in self:
            if record.total_members or record.total_leaders or record.total_leagues:
                record.total = record.total_members + record.total_leaders + record.total_leagues


    @api.depends('total_leader_fee', 'total_member_fee', 'total_league_fee')
    def _compute_totals(self):
        """This function will compute the total fee and total members"""
        for record in self:
            if record.total_member_fee or record.total_leader_fee or record.total_league_fee:
                record.total_membership_fee = record.total_leader_fee + record.total_member_fee + record.total_league_fee