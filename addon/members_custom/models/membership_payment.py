"""This file will deal with the modification of the membership payment"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

MONTHS = [
    'January',
    'February',
    'March',
    'April',
    'May',
    'June',
    'July',
    'August',
    'Septemeber',
    'October',
    'November',
    'December'
]

class PaymentFeeConfiguration(models.Model):
    _name="payment.fee.configuration"
    _description="This model will handle the configuration of payment based on income range"
    _order = "sequence, id"

    minimum_wage = fields.Float(required=True, string="Minimum Wage")
    maximum_wage = fields.Float(string="Maximum Wage")
    fee_in_percent = fields.Float(required=True, string="Fee in Percent")
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

class MembershipPayment(models.Model):
    _name="each.member.payment"
    _description="This model will handle each member's payment"
    _order = "month"

    members_payment_id = fields.Many2one('membership.payment', copy=False)
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    member_id = fields.Many2one('res.partner', domain="['|', '|', ('is_member', '=', True), ('is_leader', '=', True), ('is_league', '=', True)]", copy=False)
    subcity_id = fields.Many2one(related='members_payment_id.subcity_id', readonly=True, store=True)
    wereda_id = fields.Many2one(related='members_payment_id.wereda_id', readonly=True, store=True)
    main_office_id = fields.Many2one(related="member_id.main_office", readonly=True, store=True)
    cell_id = fields.Many2one(related="member_id.member_cells", readonly=True, store=True)
    amount_paid = fields.Float(store=True)
    amount_remaining = fields.Float(store=True, readonly=True)
    fee_amount = fields.Float(store=True, readonly=True)
    state = fields.Selection(selection=[('paid', 'Paid'), ('paid some', 'Paid Some'), ('not payed', 'Not Payed')])
    month = fields.Many2one('reconciliation.time.fream', string="Time Frame", store=True)
    year = fields.Many2one(related="month.fiscal_year", string='Year', store=True)
    annual_fee = fields.Float()
    paid_fully = fields.Boolean(default=False)
    type_of_payment = fields.Selection(selection=[('in person', 'In Person'), ('bank', 'Bank')], default='in person', required=True)
    is_league = fields.Boolean(default=False)

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
            if (record.amount_paid > 0.00) and (record.annual_fee > record.amount_paid): 
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
                

    @api.onchange('amount_paid')
    def _paid_fully(self):
        """This function will check if the paid amount is in full"""
        for record in self:
            if record.amount_paid:
                if record.amount_paid == record.annual_fee:
                    record.write({
                        'amount_remaining': 0.00,
                        'state': 'paid',
                        'paid_fully': True
                    })
                    all_payment = self.env['each.member.payment'].search([('member_id', '=', record.member_id.id), ('year', '=', record.year.id)])
                    for paid_month in all_payment:
                        paid_month.write({
                            'state': 'paid',
                            'paid_fully': True
                        })
                    all_months = self.env['reconciliation.time.fream'].search([])
                    for month in all_months:
                        if month.id not in all_payment.mapped('month').ids:
                            payment = self.env['each.member.payment'].sudo().create({
                                'member_id': record.member_id.id,
                                'main_office_id': record.member_id.main_office.id,
                                'cell_id': record.member_id.member_cells.id,
                                'fee_amount': 0.00,
                                'amount_paid': 0.00,
                                'amount_remaining': 0.00,
                                'paid_fully': True,
                                'state': 'paid',
                                'year': record.year.id,
                                'month': month.id,
                                'members_payment_id': record.members_payment_id.id,
                                'type_of_payment': record.member_id.type_of_payment,
                                'subcity_id': record.members_payment_id.subcity_id.id,
                                'wereda_id': record.members_payment_id.wereda_id.id,
                                'user_id': record.members_payment_id.user_id.id
                            })


    @api.onchange('member_id')
    def _get_from_member(self):
        """This will get the membership fee from member"""
        for record in self:
            if record.member_id:
                record.fee_amount = record.member_id.membership_monthly_fee_cash_from_percent + record.member_id.membership_monthly_fee_cash
                record.amount_paid = 0.00
                record.amount_remaining = record.fee_amount
                record.type_of_payment = record.member_id.type_of_payment
                record.annual_fee = 12 * (record.member_id.membership_monthly_fee_cash_from_percent + record.member_id.membership_monthly_fee_cash)
                if record.member_id.is_league == True:
                    record.is_league = True

    def payment_confirm(self):
        """This function will chnage state weather it has been aid or not"""
        for record in self:
            record.state = 'paid'

    def print_payslip(self):
        """This function will print payslips"""
        for record in self:
            return self.env.ref('members_custom.create_member_payment_report').report_action(record._origin.id)


class Payment(models.Model):
    _name="membership.payment"
    _description="This model will handle with the payment of memberships"


    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).parent_id.id

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    month = fields.Many2one('reconciliation.time.fream', string="Time Frame")
    year = fields.Many2one(related="month.fiscal_year", string='Year', store=True)
    amount = fields.Float(string="Amount Received")
    total_estimated = fields.Float(compute="_calculate_the_total", string="Total Estimated", store=True)
    total_paid = fields.Float(compute="_calculate_the_total", string="Total Paid", store=True)
    total_remaining = fields.Float(compute="_calculate_the_total", string="Total remaining", store=True)
    subcity_id = fields.Many2one('membership.handlers.parent', default=_default_subcity)
    wereda_id = fields.Many2one('membership.handlers.branch', default=_default_wereda)
    main_office = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]", copy=False)
    state = fields.Selection(selection=[('draft', 'Draft'), ('submit', 'Submit'), ('registered', 'Registered')], default="draft")
    member_ids = fields.One2many('each.member.payment', 'members_payment_id', copy=False)
    payment_for_supporter = fields.Boolean(default=False)
    supporter_ids = fields.Many2one('supporter.members')
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
        else:
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
                record.member_ids = [(5, 0, 0)]
                record.total_paid = 0.00
                record.total_remaining = 0.00
                record.total_estimated = 0.00

    @api.onchange('amount')
    def _make_total_amount(self):
        """This function will make the total the amount if it is supporter"""
        for record in self:
            if record.payment_for_supporter:       
                record.total_paid = record.amount
                record.total_remaining = 0.00
                record.total_estimated = 0.00

    @api.onchange('main_office')
    def _generate_members(self):
        """This field will generate members based on main_office"""
        for record in self:
            if record.main_office:
                cells = self.env['member.cells'].search([('main_office', '=', record.main_office.id)])
                for member in cells.members_ids:
                    paid_month = self.env['each.member.payment'].search([('member_id', '=', member.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                    if paid_month.id:
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
                            'year': record.year.id,
                            'month': record.month.id,
                            'members_payment_id': record.id,
                            'type_of_payment': member.type_of_payment,
                            'subcity_id': record.subcity_id.id,
                            'wereda_id': record.wereda_id.id,
                            'user_id': record.user_id.id
                        })
                        member.write({
                            'membership_payments': [(4, payment.id)],
                            'year_of_payment': record.year.id
                        })
                for member in cells.leaders_ids:
                    paid_month = self.env['each.member.payment'].search([('member_id', '=', member.id), ('year', '=', record.year.id), ('month', '=', record.month.id)])
                    if paid_month.id:
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
                            'year': record.year.id,
                            'month': record.month.id,
                            'members_payment_id': record.id,
                            'type_of_payment': member.type_of_payment,
                            'subcity_id': record.subcity_id.id,
                            'wereda_id': record.wereda_id.id,
                            'user_id': record.user_id.id
                        })
                        member.write({
                            'membership_payments': [(4, payment.id)],
                            'year_of_payment': record.year.id
                        })

    @api.depends('member_ids')
    def _calculate_the_total(self):
        for record in self:
            if not record.payment_for_supporter: 
                amount_paid = record.member_ids.mapped('amount_paid')
                estimated = record.member_ids.mapped('fee_amount')
                remaining = record.member_ids.mapped('amount_remaining')
                total_paid = 0.00
                total_estimated = 0.00
                total_remaining = 0.00
                for amount in amount_paid:
                    total_paid += amount
                record.total_paid = total_paid
                for estimate in estimated:
                    total_estimated += estimate
                record.total_estimated = total_estimated
                for remains in remaining:
                    total_remaining += remains
                record.total_remaining = total_remaining

    def submit_button(self):
        """This function will change the state of the payment"""
        for record in self:
            record.state = 'submit'

    def draft_button(self):
        """This function will revert the state of payment to draft"""
        for record in self:
            record.state = 'draft'