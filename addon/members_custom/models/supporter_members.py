"""This file will deal with the handling of supporter members"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime


class SupportingMembers(models.Model):
    _name="supporter.members"
    _description="This model will handle supporting members"


    image_1920 = fields.Binary("Image", store=True)
    # type_of_supporter = fields.Selection(selection=[('individual', 'Individual'), ('company', 'Company')], default='individual', required=True)
    # is_company = fields.Boolean(default=False)
    name = fields.Char(translate=True)
    age = fields.Integer(copy=False)
    gender = fields.Selection(selection=[('Male', 'Male'), ('Female', 'Female')])
    region = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]")
    # subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True)
    # wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", domain="[('parent_id', '=', subcity_id)]", required=True)
    # house_number = fields.Char(translate=True)
    address = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]")
    phone = fields.Char()
    education_level = fields.Many2one('res.edlevel')
    field_of_study_id = fields.Many2many('field.study')
    # education_type = fields.Selection(selection=[('formal', 'Formal'), ('informal', 'Informal'), ('non-formal', 'Non-Formal')])
    work_place = fields.Char(translate=True, copy=False)
    position = fields.Char(translate=True, copy=False)
    # income = fields.Float()
    # member_id = fields.Many2one('res.partner', readonly=True)
    # state = fields.Selection(selection=[('new', 'New'), ('approved', 'Approved')], default='new', required=True)
    payment_id = fields.Many2one('membership.payment')
    start_of_support = fields.Selection(selection=[(str(num), num) for num in range(1900, (datetime.now().year)+1 )], string='Supporter Start Year')
    # status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    status = fields.Selection(selection=[('in country', 'In Country'), ('outside of country', 'Outside of Country')], default='in country')
    gov_responsibility = fields.Char(string="Government Responsibility", translate=True, copy=False)
    # email = fields.Char()
    # website = fields.Char()
    # x_css = fields.Html(sanitize=False, compute="_compute_css", store=False)
    type_of_payment = fields.Selection(selection=[('in person', 'In Person'), ('bank', 'Bank')], default='in person')

    # @api.onchange('type_of_supporter')
    # def _make_company(self):
    #     """This function will reject candate creation"""
    #     for record in self:
    #         if record.type_of_supporter == "company":
    #             record.is_company = True
    #         else:
    #             record.is_company = False

    @api.model
    def create(self, vals):
        """This function will check if a record already exists"""
        exists = self.env['supporter.members'].search([('name', '=', vals['name']), ('gender', '=', vals['gender']), ('phone', '=', vals['phone'])])
        if exists:
            raise UserError(_("A supporter with the same name, gender and phone already exists, Please make sure it isn't a duplicated data"))
        return super(SupportingMembers, self).create(vals)

    @api.onchange('age')
    def _all_must_be_more_than_15(self):
        """This function will check if the age of the supporter is above 15"""
        for record in self:
            if record.age:
                if record.age < 15:
                    raise UserError(_("The Supporter's Age Must Be Above 15"))

    # @api.onchange('phone')
    # def _proper_phone_number(self):
    #     """This function will check if phone is of proper format"""
    #     for record in self:
    #         if record.phone:
    #             if len(record.phone) < 13:
    #                 raise UserError(_('Please Make Sure You Entered a 12 digit Phone Number with + At The Beginning'))
    #             elif record.phone[:4] != '+251':
    #                 raise UserError(_('Please Enter The Right Country Phone Code. eg +251.......')) 


    # def _compute_css(self):
    #     """This function will help remove edit button based on state"""
    #     for record in self:
    #         if self.env.user.has_group('members_custom.member_group_manager') and record.state != 'new':
    #             record.x_css = '<style> .o_form_button_edit {display:None}</style>'
    #         else:
    #             record.x_css = False


    # def create_member(self):
    #     """This function will create candidates from supporters"""
    #     for record in self:
    #         partner = self.env['res.partner'].sudo().create({
    #             'image_1920': record.image_1920,
    #             'name': record.name,
    #             'age': record.age,
    #             'gender': record.gender,
    #             'education_level': record.education_level.id,
    #             'education_type': record.education_type,
    #             'field_of_study_id': record.field_of_study_id,
    #             'region': record.region.id,
    #             'subcity_id': record.subcity_id.id,
    #             'wereda_id': record.wereda_id.id,
    #             'house_number': record.house_number,
    #             'phone': record.phone,
    #             'income': record.income,
    #             'type_of_payment': record.type_of_payment,
    #             'gov_responsibility': record.gov_responsibility,
    #             'is_member': True,
    #             'is_leader': False,
    #             'is_league': False,
    #             'was_supporter': True,
    #             'supporter_id': record.id,
    #             'was_member': True
    #         })
    #         if record.position != False and record.company_name != False:
    #             partner.write({
    #                 'work_experience_ids': [(0, 0, {
    #                     'name': record.position,
    #                     'place_of_work': record.company_name,
    #                     'current_job': True
    #                 })]
    #             })
    #         if record.income == 0.00:
    #             partner.write({
    #                 'payment_method': 'cash',
    #                 'membership_monthly_fee_percent': 0.00,
    #                 'membership_monthly_fee_cash': 0.00
    #             })
    #         else:
    #             all_fee = self.env['payment.fee.configuration'].search([])
    #             for fee in all_fee:
    #                 if fee.minimum_wage <= record.income <= fee.maximum_wage:
    #                     partner.write({
    #                         'payment_method': 'percentage',
    #                         'membership_monthly_fee_percent': fee.fee_in_percent,
    #                         'membership_monthly_fee_cash_from_percent': (fee.fee_in_percent / 100) * record.income,
    #                     })
    #                     break
    #                 else:
    #                     partner.write({
    #                         'payment_method': 'percentage',
    #                         'membership_monthly_fee_percent': fee.fee_in_percent,
    #                         'membership_monthly_fee_cash_from_percent': (fee.fee_in_percent / 100) * record.income,
    #                     })
    #                     continue
    #         name = partner.name.split()[0] + partner.phone[-4:]
    #         existing = self.env['res.users'].sudo().search([('login', '=', name)])
    #         if existing:
    #             name = partner.name.split()[0] + partner.phone[-9:]
    #             self.env['res.users'].create({
    #                 'partner_id': partner.id,
    #                 'login': name,
    #                 'password': '123456',
    #                 'groups_id': [self.env.ref('base.group_portal').id],
    #             })
    #         else:
    #             self.env['res.users'].create({
    #                 'partner_id': partner.id,
    #                 'login': name,
    #                 'password': '123456',
    #                 'groups_id': [self.env.ref('base.group_portal').id],
    #             })
    #         record.state = 'approved'
    #         record.member_id = partner.id
