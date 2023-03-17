"""This file will deal with the modification of the membership payment"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

original = 0.00

class PaymentFeeConfiguration(models.Model):
    _name="payment.fee.configuration"
    _description="This model will handle the configuration of payment based on income range"
    _order = "sequence, id"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    minimum_wage = fields.Float(required=True, string="Minimum Wage", track_visibility='onchange')
    maximum_wage = fields.Float(string="Maximum Wage", track_visibility='onchange')
    fee_in_percent = fields.Float(required=True, string="Fee in Percent", track_visibility='onchange')
    sequence = fields.Integer(default=1)

    _sql_constraints = [
                    ('check_on_maximum_wage', 'CHECK(maximum_wage > 0 AND maximum_wage > minimum_wage)', 'Maximum wage must be more than Minimum Wage and 1'),
                    ('check_on_minimum_wage', 'CHECK(minimum_wage > 0 AND minimum_wage < maximum_wage)', 'Minimum wage must be less than Maximum Wage and greater than 1'),
                    ('check_on_fee_in_percent', 'CHECK(fee_in_percent <= 100)', 'Fee in Percent Must be Less Than 100')
                    ]


    @api.onchange('minimum_wage', 'maximum_wage')
    def _check_database_for_existing_record(self):
        """This function will make sure there is no repeation of wages in database"""
        for record in self:
            all_fee = self.env['payment.fee.configuration'].search([])
            for fee in all_fee:
                if (fee.minimum_wage <= record.minimum_wage <= fee.maximum_wage) or (fee.minimum_wage <= record.maximum_wage <= fee.maximum_wage):
                    message = "Configuration for this wage already exists."
                    raise UserError(_(message))

class LeaguePayment(models.Model):
    _name="each.league.payment"
    _description="This model will handle each league's payment"
    _order = "month"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    members_payment_id = fields.Many2one('membership.payment', copy=False, track_visibility='onchange')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one(related='members_payment_id.subcity_id', readonly=True, store=True)
    wereda_id = fields.Many2one(related='members_payment_id.wereda_id', readonly=True, store=True, track_visibility='onchange')
    league_id = fields.Many2one('res.partner', domain="['&', ('wereda_id', '=', wereda_id),'|', '|', ('is_member', '=', True), ('is_leader', '=', True), ('is_league', '=', True)]", copy=False)
    main_office_id = fields.Many2one(related="league_id.main_office", readonly=True, store=True)
    cell_id = fields.Many2one(related="league_id.member_cells", readonly=True, store=True)
    amount_paid = fields.Float(store=True, default=0.00, track_visibility='onchange')
    amount_remaining = fields.Float(store=True, readonly=True)
    fee_amount = fields.Float(store=True, readonly=True)
    state = fields.Selection(selection=[('paid', 'Paid'), ('paid some', 'Paid Some'), ('not payed', 'Not Payed')], track_visibility='onchange')
    traced_league_payment = fields.Float(string="Tracked Payment", store=True)
    month = fields.Many2one('reconciliation.time.fream', string="Time Frame", store=True, track_visibility='onchange')
    year = fields.Many2one(related="month.fiscal_year", string='Year', store=True, track_visibility='onchange')
    league_type = fields.Selection(related="league_id.league_type", readonly=True, store=True)
    league_org = fields.Selection(related="league_id.league_org", readonly=True, store=True)
    annual_league_fee = fields.Float()
    paid_fully = fields.Boolean(default=False)
    type_of_payment = fields.Selection(related="league_id.type_of_payment", readonly=True, store=True)
    original = fields.Float()
    id_payment = fields.Float(track_visibility='onchange')
    paid_for_id = fields.Boolean(default=False, track_visibility='onchange')

    @api.model
    def create(self, vals):
        """This function will create a league payment and delete an exisitng one"""
        month = self.env['reconciliation.time.fream'].search([('id', '=', vals['month'])])
        payment = self.env['each.league.payment'].search([('month', '=', vals['month']), ('year', '=', month.fiscal_year.id), ('league_id', '=', vals['league_id'])])
        if payment:
            payment.write({
                'state': 'paid'
            })
            return payment
        else:
            return super(LeaguePayment, self).create(vals)

    @api.onchange('amount_paid')
    def _compute_remaining_for_league(self):
        """This function will compute the remaining amount"""
        for record in self:
            if (record.amount_paid > 0.00) and (record.annual_league_fee >= record.amount_paid): 
                if (record.amount_paid >= record.fee_amount):
                    record.write({
                        'amount_remaining': 0.00,
                        'state': 'paid'
                    })
                else:
                    record.write({
                        'amount_remaining': record.fee_amount - record.amount_paid,
                        'state': 'paid some'
                    })


    @api.onchange('league_id')
    def _get_from_league(self):
        """This will get the membership fee from league"""
        for record in self:
            if record.league_id:
                record.fee_amount = record.league_id.league_payment
                record.amount_remaining = record.fee_amount
                record.annual_league_fee = 12 * record.fee_amount


    def print_league_payslip(self):
        """This function will print payslips"""
        for record in self:
            return self.env.ref('members_custom.create_league_payment_report').report_action(record._origin.id)

class MembershipPayment(models.Model):
    _name="each.member.payment"
    _description="This model will handle each member's payment"
    _order = "month"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    members_payment_id = fields.Many2one('membership.payment', copy=False)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    subcity_id = fields.Many2one(related='members_payment_id.subcity_id', readonly=True, store=True)
    wereda_id = fields.Many2one(related='members_payment_id.wereda_id', readonly=True, store=True)
    member_id = fields.Many2one('res.partner', domain="['&', ('wereda_id', '=', wereda_id),'|', '|', ('is_member', '=', True), ('is_leader', '=', True), ('is_league', '=', False)]", copy=False, track_visibility='onchange')
    main_office_id = fields.Many2one(related="member_id.main_office", readonly=True, store=True)
    cell_id = fields.Many2one(related="member_id.member_cells", readonly=True, store=True)
    amount_paid = fields.Float(store=True, default=0.00, track_visibility='onchange')
    amount_remaining = fields.Float(store=True, readonly=True)
    fee_amount = fields.Float(store=True, readonly=True)
    traced_member_payment = fields.Float(string="Tracked Payment", store=True)
    state = fields.Selection(selection=[('paid', 'Paid'), ('paid some', 'Paid Some'), ('not payed', 'Not Payed')], track_visibility='onchange')
    month = fields.Many2one('reconciliation.time.fream', string="Time Frame", store=True, track_visibility='onchange')
    year = fields.Many2one(related="month.fiscal_year", string='Year', store=True, track_visibility='onchange')
    annual_fee = fields.Float()
    paid_fully = fields.Boolean(default=False)
    type_of_payment = fields.Selection(related="member_id.type_of_payment", readonly=True, store=True)
    original = fields.Float()
    id_payment = fields.Float(track_visibility='onchange')
    paid_for_id = fields.Boolean(default=False, track_visibility='onchange')

    @api.model
    def create(self, vals):
        """This function will create a member payment and delete an exisitng one"""
        month = self.env['reconciliation.time.fream'].search([('id', '=', vals['month'])])
        payment = self.env['each.member.payment'].search([('month', '=', vals['month']), ('year', '=', month.fiscal_year.id), ('member_id', '=', vals['member_id'])])
        if payment:
            payment.write({
                'state': 'paid'
            })
            return payment
        else:
            return super(MembershipPayment, self).create(vals)

    @api.onchange('amount_paid')
    def _compute_remaining(self):
        """This function will compute the remaining amount"""
        for record in self:           
            if (record.amount_paid > 0.00) and (record.annual_fee >= record.amount_paid):
                if (record.amount_paid >= record.fee_amount):
                    record.write({
                        'amount_remaining': 0.00,
                        'state': 'paid'
                    })                 
                else:                   
                    record.write({
                        'amount_remaining': record.fee_amount - record.amount_paid,
                        'state': 'paid some'
                    })


    @api.onchange('member_id')
    def _get_from_member(self):
        """This will get the membership fee from member"""
        for record in self:
            if record.member_id:
                record.fee_amount = record.member_id.membership_monthly_fee_cash_from_percent + record.member_id.membership_monthly_fee_cash
                record.amount_remaining = record.fee_amount
                record.annual_fee = 12 * (record.member_id.membership_monthly_fee_cash_from_percent + record.member_id.membership_monthly_fee_cash)

    def print_payslip(self):
        """This function will print payslips"""
        for record in self:
            return self.env.ref('members_custom.create_member_payment_report').report_action(record._origin.id)

    def print_id(self):
        """This function will print payslip for ID"""
        for record in self:
            return self.env.ref('members_custom.membership_id_payment_report').report_action(record._origin.id)


class Payment(models.Model):
    _name="membership.payment"
    _description="This model will handle with the payment of memberships"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).parent_id.id

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    year = fields.Many2one("fiscal.year", string='Year', store=True, track_visibility='onchange')
    month = fields.Many2one('reconciliation.time.fream', domain="[('fiscal_year', '=', year)]", string="Time Frame", track_visibility='onchange')
    amount = fields.Float(string="Amount Received", track_visibility='onchange')
    total_estimated = fields.Float(compute="_get_total", string="Total Estimated", store=True, readonly=True)
    total_paid = fields.Float(compute="_get_paid_total", string="Total Paid", store=True, readonly=True)
    total_remaining = fields.Float(compute="_get_total", string="Total remaining", store=True, readonly=True)
    subcity_id = fields.Many2one('membership.handlers.parent',default=_default_subcity, domain="[('branch_ids.branch_manager', '=', user_id)]", track_visibility='onchange')
    wereda_id = fields.Many2one('membership.handlers.branch', default=_default_wereda, domain="[('parent_id', '=', subcity_id)]", track_visibility='onchange')
    payment_for_league_member = fields.Selection(selection=[('member', 'Member'), ('league', 'League')], default='member', required=True)
    main_office = fields.Many2one('main.office', domain="['&', ('for_which_members', '=', payment_for_league_member), ('wereda_id', '=', wereda_id)]", copy=False, track_visibility='onchange')
    state = fields.Selection(selection=[('draft', 'Draft'), ('submit', 'Submit'), ('registered', 'Registered')], default="draft")
    member_ids = fields.One2many('each.member.payment', 'members_payment_id', copy=False, track_visibility='onchange')
    total_estimated_for_members = fields.Float(compute="_compute_members_fees", string="Members' Estimated", store=True)
    total_paid_for_members = fields.Float(compute="_compute_members_fees", string="Members' Paid", store=True)
    total_remaining_for_members = fields.Float(compute="_compute_members_fees", string="Members' Remaining", store=True)
    total_id_payments_members = fields.Float(compute="_compute_members_fees", string="Members' ID Payment", store=True)
    league_ids = fields.One2many('each.league.payment', 'members_payment_id', copy=False, track_visibility='onchange')
    total_estimated_for_leagues = fields.Float(compute="_compute_leagues_fees", string="Leagues' Estimated", store=True)
    total_paid_for_leagues = fields.Float(compute="_get_paid_total", string="Leagues' Paid", store=True)
    total_remaining_for_leagues = fields.Float(compute="_compute_leagues_fees", string="Leagues' Remaining", store=True)
    total_id_payments_leagues = fields.Float(compute="_compute_leagues_fees", string="Leagues' ID Payment", store=True)
    payment_for_supporter = fields.Boolean(default=False)
    donor_supporter = fields.Selection(selection=[('donor', 'Donor'), ('supporter', 'Supporter')], default='donor', track_visibility='onchange')
    donors_id = fields.Many2one('donors', track_visibility='onchange')
    supporter_ids = fields.Many2one('supporter.members', domain="[('wereda_id', '=', wereda_id)]", track_visibility='onchange')
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)


    def _compute_css(self):
        """This function will help remove edit button based on state"""
        for record in self:
            if record.state == 'submit':
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False

    @api.model
    def create(self, vals):
        """This function will create a payment and save it as a draft"""
        if vals['payment_for_supporter'] == True:
            vals['name'] = self.env['ir.sequence'].next_by_code('supporter.members')
        if vals['payment_for_supporter'] == False:
            vals['name'] = self.env['ir.sequence'].next_by_code('membership.payment')
        vals['state'] = 'draft'
        return super(Payment, self).create(vals)

    @api.onchange('payment_for_supporter')
    def _main_office_removed(self):
        """This function will make null for those not to be in supporter"""
        for record in self:
            if record.payment_for_supporter:
                record.main_office = False
                for memb in record.member_ids:
                    memb.unlink()
                for league in record.league_ids:
                    league.unlink()
                record.member_ids = [(5, 0, 0)]
                record.league_ids = [(5, 0, 0)]
                record.total_paid = 0.00
                record.total_remaining = 0.00
                record.total_estimated = 0.00
                record.total_estimated_for_members = 0.00
                record.total_paid_for_members = 0.00
                record.total_remaining_for_members = 0.00
                record.total_estimated_for_leagues = 0.00
                record.total_paid_for_leagues = 0.00
                record.total_remaining_for_leagues = 0.00


    @api.onchange('amount')
    def _make_total_amount(self):
        """This function will make the total the amount if it is supporter"""
        for record in self:
            if record.payment_for_supporter:       
                record.total_paid = record.amount
                record.total_remaining = 0.00
                record.total_estimated = 0.00

    @api.depends('member_ids')
    def _compute_members_fees(self):
        """This function will computethe fees for members"""
        for record in self:
            if record.member_ids:
                record.total_estimated_for_members = sum(record.member_ids.mapped('fee_amount'))
                record.total_remaining_for_members = sum(record.member_ids.mapped('amount_remaining'))
                record.total_id_payments_members = sum(record.member_ids.mapped('id_payment'))
                record.total_paid_for_members = sum(record.member_ids.mapped('amount_paid'))

    @api.depends('league_ids')
    def _compute_leagues_fees(self):
        """This function will computethe fees for members"""
        for record in self:
            if record.league_ids:
                record.total_estimated_for_leagues = sum(record.league_ids.mapped('fee_amount'))
                record.total_remaining_for_leagues = sum(record.league_ids.mapped('amount_remaining'))                
                record.total_id_payments_leagues = sum(record.league_ids.mapped('id_payment'))
                record.total_paid_for_leagues = sum(record.league_ids.mapped('amount_paid'))


    # @api.depends('total_paid_for_leagues', 'total_id_payments_leagues', 'total_paid_for_members', 'total_id_payments_members')
    # def _get_paid_total(self):
    #     """This function will get the total paid"""
    #     for record in self:
    #         if record.total_paid_for_leagues or record.total_id_payments_leagues:
    #             record.total_paid = record.total_paid_for_leagues + record.total_id_payments_leagues
    #         if record.total_paid_for_members or record.total_id_payments_members:
    #             record.total_paid = record.total_paid_for_members + record.total_id_payments_members

    # @api.depends('member_ids', 'league_ids')
    # def _get_total(self):
    #     """This function will get the total estimated and remianing"""
    #     for record in self:
    #         if record.member_ids:
    #             record.total_estimated = sum(record.member_ids.mapped('fee_amount'))
    #             record.total_remaining = sum(record.member_ids.mapped('amount_remaining'))
    #         if record.league_ids:
    #             record.total_estimated = sum(record.league_ids.mapped('fee_amount'))
    #             record.total_remaining = sum(record.league_ids.mapped('amount_remaining'))                  

    @api.onchange('main_office')
    def _generate_members(self):
        """This field will generate members based on main_office"""
        for record in self:
            if record.main_office:                
                if not record.month or not record.year:
                    raise UserError(_('Please Fill In The Year and Month First.'))
                all_payments = self.env['membership.payment'].search([('year', '=', record.year.id), ('month', '=', record.month.id), ('main_office', '=', record.main_office.id)])
                if all_payments:
                    message = "A payment for " + str(record.main_office.name) + " for the " + str(record.month.name) + " month and " + str(record.year.name) + " year already exists. Please use that payment method in draft state."
                    raise UserError(_(message))
                if record.member_ids:
                    record.member_ids = [(5, 0, 0)]
                if record.league_ids:
                    record.league_ids = [(5, 0, 0)]
                if record.payment_for_league_member == 'member':
                    cells = self.env['member.cells'].search([('main_office', '=', record.main_office.id)])
                    for member in cells.members_ids:
                        if member.pay_for_league == True:
                            paid_month = self.env['each.league.payment'].search([('league_id', '=', member.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                            if paid_month.id:
                                paid_month.write({
                                    'members_payment_id': record._origin.id,
                                    'subcity_id': record.subcity_id.id,
                                    'wereda_id': record.wereda_id.id,
                                    'user_id': record.user_id.id,
                                    'main_office_id': member.main_office.id,
                                    'cell_id': member.member_cells.id, 
                                    'traced_league_payment': member.track_league_fee                           
                                })
                                record.write({
                                    'league_ids': [(4, paid_month.id)]
                                })
                            else:
                                payment = self.env['each.league.payment'].sudo().create({
                                    'league_id': member.id,
                                    'main_office_id': member.main_office.id,
                                    'cell_id': member.member_cells.id,
                                    'fee_amount': member.league_payment,
                                    'amount_remaining': member.league_payment,
                                    'amount_paid': 0.00,
                                    'state': 'not payed',
                                    'annual_league_fee': 12 * (member.league_payment),
                                    'traced_league_payment': member.track_league_fee,
                                    'year': record.year.id,
                                    'month': record.month.id,
                                    'members_payment_id': record.id,
                                    'type_of_payment': member.type_of_payment,
                                    'subcity_id': record.subcity_id.id,
                                    'wereda_id': record.wereda_id.id,
                                    'user_id': record.user_id.id,
                                    'id_payment': 0.00
                                })
                                member.write({
                                    'league_payments': [(4, payment.id)],
                                    'year_of_payment': payment.year.id
                                })
                        paid_month = self.env['each.member.payment'].search([('member_id', '=', member.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                        if paid_month.id:
                            paid_month.write({
                                'members_payment_id': record._origin.id,
                                'subcity_id': record.subcity_id.id,
                                'wereda_id': record.wereda_id.id,
                                'user_id': record.user_id.id,
                                'main_office_id': member.main_office.id,
                                'cell_id': member.member_cells.id,
                                'traced_member_payment': member.track_member_fee                         
                            })
                            record.write({
                                'member_ids': [(4, paid_month.id)]
                            })
                        else:    
                            payment = self.env['each.member.payment'].sudo().create({
                                'member_id': member.id,
                                'main_office_id': member.main_office.id,
                                'cell_id': member.member_cells.id,
                                'fee_amount': member.membership_monthly_fee_cash + member.membership_monthly_fee_cash_from_percent,
                                'amount_remaining': member.membership_monthly_fee_cash + member.membership_monthly_fee_cash_from_percent,
                                'amount_paid': 0.00,
                                'state': 'not payed',
                                'annual_fee': 12 * (member.membership_monthly_fee_cash + member.membership_monthly_fee_cash_from_percent),
                                'traced_member_payment': member.track_member_fee,
                                'year': record.year.id,
                                'month': record.month.id,
                                'members_payment_id': record.id,
                                'type_of_payment': member.type_of_payment,
                                'subcity_id': record.subcity_id.id,
                                'wereda_id': record.wereda_id.id,
                                'user_id': record.user_id.id,
                                'id_payment': 0.00
                            })
                            member.write({
                                'membership_payments': [(4, payment.id)],
                                'year_of_payment': payment.year.id
                            })
                    for leader in cells.leaders_ids:
                        if leader.pay_for_league == True:
                            paid_month = self.env['each.league.payment'].search([('league_id', '=', leader.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                            if paid_month.id:
                                paid_month.write({
                                    'members_payment_id': record._origin.id,
                                    'subcity_id': record.subcity_id.id,
                                    'wereda_id': record.wereda_id.id,
                                    'user_id': record.user_id.id,
                                    'main_office_id': leader.main_office.id,
                                    'cell_id': leader.member_cells.id,
                                    'traced_league_payment': leader.track_league_fee                            
                                })
                                record.write({
                                    'league_ids': [(4, paid_month.id)]
                                })
                            else:
                                payment = self.env['each.league.payment'].sudo().create({
                                    'league_id': leader.id,
                                    'main_office_id': leader.main_office.id,
                                    'cell_id': leader.member_cells.id,
                                    'fee_amount': leader.league_payment,
                                    'amount_remaining': leader.league_payment,
                                    'amount_paid': 0.00,
                                    'state': 'not payed',
                                    'annual_league_fee': 12 * (leader.league_payment),
                                    'traced_league_payment': leader.track_league_fee,
                                    'year': record.year.id,
                                    'month': record.month.id,
                                    'members_payment_id': record.id,
                                    'type_of_payment': leader.type_of_payment,
                                    'subcity_id': record.subcity_id.id,
                                    'wereda_id': record.wereda_id.id,
                                    'user_id': record.user_id.id,
                                    'id_payment': 0.00
                                })
                                leader.write({
                                    'league_payments': [(4, payment.id)],
                                    'year_of_payment': payment.year.id
                                })
                        paid_month = self.env['each.member.payment'].search([('member_id', '=', leader.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                        if paid_month.id:
                            paid_month.write({
                                'members_payment_id': record._origin.id,
                                'subcity_id': record.subcity_id.id,
                                'wereda_id': record.wereda_id.id,
                                'user_id': record.user_id.id,
                                'main_office_id': leader.main_office.id,
                                'cell_id': leader.member_cells.id,
                                'traced_member_payment': leader.track_member_fee                          
                            })
                            record.write({
                                'member_ids': [(4, paid_month.id)]
                            })
                        else:    
                            payment = self.env['each.member.payment'].sudo().create({
                                'member_id': leader.id,
                                'main_office_id': leader.main_office.id,
                                'cell_id': leader.member_cells.id,
                                'fee_amount': leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent,
                                'amount_remaining': leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent,
                                'amount_paid': 0.00,
                                'state': 'not payed',
                                'annual_fee': 12 * (leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent),
                                'traced_member_payment': leader.track_member_fee,
                                'year': record.year.id,
                                'month': record.month.id,
                                'members_payment_id': record.id,
                                'type_of_payment': leader.type_of_payment,
                                'subcity_id': record.subcity_id.id,
                                'wereda_id': record.wereda_id.id,
                                'user_id': record.user_id.id,
                                'id_payment': 0.00
                            })
                            leader.write({
                                'membership_payments': [(4, payment.id)],
                                'year_of_payment': payment.year.id
                            })
                if record.payment_for_league_member == 'league':
                    cells = self.env['member.cells'].search([('main_office_league', '=', record.main_office.id)])
                    for league in cells.leagues_ids:
                        paid_month = self.env['each.league.payment'].search([('league_id', '=', league.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                        if paid_month.id:
                            paid_month.write({
                                'members_payment_id': record._origin.id,
                                'subcity_id': record.subcity_id.id,
                                'wereda_id': record.wereda_id.id,
                                'user_id': record.user_id.id,
                                'main_office_id': league.main_office.id,
                                'cell_id': league.member_cells.id,
                                'traced_league_payment': league.track_league_fee,
                                'league_type': league.league_type,
                                'league_org': league.league_org                           
                            })
                            record.write({
                                'league_ids': [(4, paid_month.id)]
                            })
                        else:    
                            payment = self.env['each.league.payment'].sudo().create({
                                'league_id': league.id,
                                'main_office_id': league.main_office.id,
                                'cell_id': league.member_cells.id,
                                'fee_amount': league.league_payment,
                                'amount_remaining': league.league_payment,
                                'amount_paid': 0.00,
                                'state': 'not payed',
                                'annual_league_fee': 12 * (league.league_payment),
                                'traced_league_payment': league.track_league_fee,
                                'year': record.year.id,
                                'month': record.month.id,
                                'members_payment_id': record.id,
                                'type_of_payment': league.type_of_payment,
                                'subcity_id': record.subcity_id.id,
                                'wereda_id': record.wereda_id.id,
                                'user_id': record.user_id.id,
                                'league_type': league.league_type,
                                'league_org': league.league_org,
                                'id_payment': 0.00
                            })
                            league.write({
                                'league_payments': [(4, payment.id)],
                                'year_of_payment': payment.year.id
                            })
                    for league in cells.league_leaders_ids:
                        paid_month = self.env['each.league.payment'].search([('league_id', '=', league.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                        if paid_month.id:
                            paid_month.write({
                                'members_payment_id': record._origin.id,
                                'subcity_id': record.subcity_id.id,
                                'wereda_id': record.wereda_id.id,
                                'user_id': record.user_id.id,
                                'main_office_id': league.main_office.id,
                                'cell_id': league.member_cells.id,
                                'traced_league_payment': league.track_league_fee,
                                'league_type': league.league_type,
                                'league_org': league.league_org                           
                            })
                            record.write({
                                'league_ids': [(4, paid_month.id)]
                            })
                        else:    
                            payment = self.env['each.league.payment'].sudo().create({
                                'league_id': league.id,
                                'main_office_id': league.main_office.id,
                                'cell_id': league.member_cells.id,
                                'fee_amount': league.league_payment,
                                'amount_remaining': league.league_payment,
                                'amount_paid': 0.00,
                                'state': 'not payed',
                                'annual_league_fee': 12 * (league.league_payment),
                                'traced_league_payment': league.track_league_fee,
                                'year': record.year.id,
                                'month': record.month.id,
                                'members_payment_id': record.id,
                                'type_of_payment': league.type_of_payment,
                                'subcity_id': record.subcity_id.id,
                                'wereda_id': record.wereda_id.id,
                                'user_id': record.user_id.id,
                                'league_type': league.league_type,
                                'league_org': league.league_org,
                                'id_payment': 0.00
                            })
                            league.write({
                                'league_payments': [(4, payment.id)],
                                'year_of_payment': payment.year.id
                            })                    

    def submit_button(self):
        """This function will change the state of the payment"""
        for record in self:
            if record.amount == 0.00:
                raise UserError(_("Please Add The Amount Paid"))
            for payment in record.member_ids:
                if payment.id_payment > 0.00:
                    payment.paid_for_id = True
                    payment.member_id.write({
                        'payed_for_id': True
                    })                   
                if (payment.annual_fee > payment.amount_paid) and (payment.paid_fully == False):
                    trace = payment.amount_paid - payment.fee_amount
                    payment.original = payment.traced_member_payment
                    payment.traced_member_payment += trace
                    payment.member_id.track_member_fee = payment.traced_member_payment
                if (payment.amount_paid == payment.annual_fee) and (payment.amount_paid > 0.00):
                    payment.write({
                        'amount_remaining': 0.00,
                        'state': 'paid',
                        'paid_fully': True
                    })
                    all_payment = self.env['each.member.payment'].search([('member_id', '=', payment.member_id.id), ('year', '=', payment.year.id)])
                    if all_payment:
                        for paid_month in all_payment:
                            paid_month.write({
                                'state': 'paid',
                                'paid_fully': True
                            })
                    all_months = self.env['reconciliation.time.fream'].search([('fiscal_year', '=', payment.year.id)])
                    for month in all_months:
                        if month.id not in all_payment.mapped('month').ids:
                            payment = self.env['each.member.payment'].sudo().create({
                                'member_id': payment.member_id.id,
                                'fee_amount': payment.member_id.membership_monthly_fee_cash + payment.member_id.membership_monthly_fee_cash_from_percent,
                                'amount_paid': 0.00,
                                'amount_remaining': 0.00,
                                'annual_fee': 12 * (payment.member_id.membership_monthly_fee_cash + payment.member_id.membership_monthly_fee_cash_from_percent),
                                'paid_fully': True,
                                'state': 'paid',
                                'year': payment.year.id,
                                'month': month.id,
                                'type_of_payment': payment.member_id.type_of_payment
                            })
            for payment in record.league_ids:
                if payment.id_payment > 0.00:
                    payment.paid_for_id = True
                    payment.league_id.write({
                        'payed_for_id': True
                    })
                if (payment.annual_league_fee > payment.amount_paid) and (payment.paid_fully == False):
                    trace = payment.amount_paid - payment.fee_amount
                    payment.original = payment.traced_league_payment
                    payment.traced_league_payment += trace
                    payment.league_id.track_league_fee = payment.traced_league_payment
                if (payment.amount_paid == payment.annual_league_fee) and (payment.amount_paid > 0.00):
                    payment.write({
                        'amount_remaining': 0.00,
                        'state': 'paid',
                        'paid_fully': True
                    })
                    all_payment = self.env['each.league.payment'].search([('league_id', '=', payment.league_id.id), ('year', '=', payment.year.id)])
                    for paid_month in all_payment:
                        paid_month.write({
                            'state': 'paid',
                            'paid_fully': True
                        })
                    all_months = self.env['reconciliation.time.fream'].search([('fiscal_year', '=', payment.year.id)])
                    for month in all_months:
                        if month.id not in all_payment.mapped('month').ids:
                            payment = self.env['each.league.payment'].sudo().create({
                                'league_id': payment.league_id.id,
                                'fee_amount': payment.league_id.league_payment,
                                'amount_paid': 0.00,
                                'amount_remaining': 0.00,
                                'annual_league_fee': 12 * payment.league_id.league_payment,
                                'paid_fully': True,
                                'state': 'paid',
                                'year': payment.year.id,
                                'month': month.id,
                                'type_of_payment': payment.league_id.type_of_payment
                            })
            record.state = 'submit'

    def draft_button(self):
        """This function will revert the state of payment to draft"""
        for record in self:
            for payment in record.member_ids:
                if (payment.annual_fee > payment.amount_paid) and (payment.paid_fully == False):
                    payment.traced_member_payment = payment.original
                    payment.member_id.track_member_fee = payment.original
                if (payment.amount_paid == payment.annual_fee) and (payment.amount_paid > 0.00):
                    all_payment = self.env['each.member.payment'].search([('member_id', '=', payment.member_id.id), ('year', '=', payment.year.id)])
                    all_months = self.env['reconciliation.time.fream'].search([('fiscal_year', '=', payment.year.id)])
                    for month in all_months:
                        if month.id <= payment.month.id:
                            past_payment = all_payment.filtered(lambda rec: rec.month.id == month.id)
                            past_payment.write({
                                'state': 'not payed',
                                'paid_fully': False
                            })
                        else:
                            generated = all_payment.filtered(lambda rec: rec.month.id == month.id)
                            generated.unlink()
                            all_payment = self.env['each.member.payment'].search([('member_id', '=', payment.member_id.id), ('year', '=', payment.year.id)])
            for payment in record.league_ids:
                if (payment.annual_league_fee > payment.amount_paid) and (payment.paid_fully == False):
                    payment.traced_league_payment = payment.original
                    payment.league_id.track_league_fee = payment.original
                if (payment.amount_paid == payment.annual_league_fee) and (payment.amount_paid > 0.00):
                    all_payment = self.env['each.league.payment'].search([('league_id', '=', payment.league_id.id), ('year', '=', payment.year.id)])
                    all_months = self.env['reconciliation.time.fream'].search([('fiscal_year', '=', payment.year.id)])
                    for month in all_months:
                        if month.id <= payment.month.id:
                            past_payment = all_payment.filtered(lambda rec: rec.month.id == month.id)
                            past_payment.write({
                                'state': 'not payed',
                                'paid_fully': False
                            })
                        else:
                            generated = all_payment.filtered(lambda rec: rec.month.id == month.id)
                            generated.unlink()
                            all_payment = self.env['each.league.payment'].search([('league_id', '=', payment.league_id.id), ('year', '=', payment.year.id)])
            record.state = 'draft'

    def print_supporter_payslip(self):
        """This function will print payslips"""
        for record in self:
            return self.env.ref('members_custom.create_supporter_payment_report').report_action(record._origin.id)