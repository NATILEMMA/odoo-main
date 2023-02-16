"""This file will deal with the candidate members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ethiopian_date import EthiopianDateConverter

class CandidateMembers(models.Model):
    _name="candidate.members"
    _description="This model will handle candidate members"

    image_1920 = fields.Binary("Image", store=True)
    name = fields.Char(required=True, translate=True)
    age = fields.Integer(required=True)
    date = fields.Date(index=True)
    gender = fields.Selection(selection=[('Male', 'Male'), ('Female', 'Female')], copy=False, required=True)
    region = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]")
    education_level = fields.Many2one('res.edlevel', required=True)
    education_type = fields.Selection(selection=[('formal', 'Formal'), ('informal', 'Informal'), ('non-formal', 'Non-Formal')])
    other_trainings = fields.Char(translate=True)
    source_of_livelihood = fields.Selection(selection=[('governmental', 'Governmental'), ('private', 'Private'), ('individual', 'Individual'), ('stay at home', 'Stay At Home')])
    company_name = fields.Char(translate=True)
    position = fields.Char(translate=True)
    income = fields.Float()
    years_of_service = fields.Char(translate=True)
    city = fields.Char(translate=True)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True)
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True)
    house_number = fields.Char()
    house_phone_number = fields.Char()
    office_phone_number = fields.Char()
    phone = fields.Char(required=True)
    previous_membership = fields.Boolean(default=False, string="Previous Political Membership")
    partner_id = fields.Many2one('res.partner', readonly=True)
    state = fields.Selection(selection=[('new', 'New'), ('approved', 'Approved')], default='new', required=True)
    x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    becomes_member_on = fields.Date(string="Becomes Member On")
    new_member = fields.Boolean(default=False)


    @api.model
    def create(self, vals):
        """This function will compute the becomes_member_on"""
        res = super(CandidateMembers, self).create(vals)
        res.becomes_member_on = res.create_date + relativedelta(months=6)
        return res
    #     string = str(res.becomes_member_on).split(' ')[0]
    #     date_time_obj = string.split('-')
    #     Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
    #     res.ethiopian_date_two = Edate
    #     if res.date:
    #         date_str = str(res.date).split(' ')[0]
    #         date_time_obj = date_str.split('-')
    #         Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
    #         res.ethiopian_date = Edate

    # def write(self, vals):
    #     try:
    #         if vals['becomes_member_on'] is not None:
    #             date_str = str(vals['becomes_member_on']).split(' ')[0]
    #             date_time_obj = date_str.split('-')
    #             Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
    #             vals['ethiopian_date_two'] = Edate
    #     except:
    #         pass
    #     try:
    #         if vals['date'] is not None:
    #             date_str = str(vals['date']).split(' ')[0]
    #             date_time_obj = date_str.split('-')
    #             Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
    #             vals['ethiopian_date'] = Edate
    #     except:
    #         pass
    #     return super(CandidateMembers, self).write(vals) 

    def make_member_button_appear(self):
        """This function will check if today is becomes_member_on"""
        all_candidate = self.env['candidate.members'].search([('becomes_member_on', '<=', date.today()), ('state', '=', 'new')])
        if all_candidate:
            for candidate in all_candidate:
                candidate.write({'new_member': True})

    # @api.depends('date')
    # def _create_eth_bday(self):
    #     """This function will find the ethiopian birth day"""
    #     for record in self:
    #         if record.date:
    #             string = str(record.date).split(' ')[0]
    #             date_time_obj = string.split('-')
    #             Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
    #             record.ethiopian_date = Edate

    @api.onchange('source_of_livelihood')
    def _remove_data(self):
       """This function will remove data if source_of_livelihood is stay at home"""
       for record in self:
           if record.source_of_livelihood == 'stay at home':
               record.company_name = ''
               record.position = ''
               record.income = 0.0
               record.years_of_service = ''

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
            if self.env.user.has_group('members_custom.member_group_manager') and record.state != 'new':
                record.x_css = '<style> .o_form_button_edit {display:None}</style>'
            else:
                record.x_css = False


    def create_members(self):
        """This function will create members from candidates"""
        for record in self:
            partner = self.env['res.partner'].sudo().create({
                'image_1920': record.image_1920,
                'name': record.name,
                'gender': record.gender,
                'age': record.age,
                'region': record.region.id,
                'education_level': record.education_level.id,
                'income': record.income,
                'subcity_id': record.subcity_id.id,
                'wereda_id': record.wereda_id.id,
                'phone': record.phone,
                'was_candidate': True,
                'was_member': True
            })
            if record.position == False and record.company_name == False and record.years_of_service == False:
                partner.write({
                    'is_member': True,
                    'is_leader': False,
                    'is_league': False,
                })
            else:
                partner.write({
                    'work_experience_ids': [(0, 0, {
                        'name': record.position,
                        'place_of_work': record.company_name,
                        'years_of_service': record.years_of_service,
                        'current_job': True
                    })],
                    'is_member': True,
                    'is_leader': False,
                    'is_league': False,
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
            name = partner.name.split()[0] + partner.phone[-4:]
            existing = self.env['res.users'].sudo().search([('login', '=', name)])
            if existing:
                name = partner.name.split()[0] + partner.phone[-9:]
                partner.user_name = name
                self.env['res.users'].create({
                    'partner_id': partner.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            else:
                partner.user_name = name
                self.env['res.users'].create({
                    'partner_id': partner.id,
                    'login': name,
                    'password': '123456',
                    'groups_id': [self.env.ref('base.group_portal').id],
                })
            record.state = 'approved'
            record.partner_id = partner.id
