"""This file will deal with the handling of donors"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime


class Donors(models.Model):
    _name="donors"
    _description="This model will handle Donors members"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']


    image_1920 = fields.Binary("Image", store=True)
    type_of_supporter = fields.Selection(selection=[('individual', 'Individual'), ('company', 'Company')], default='individual')
    is_company = fields.Boolean(default=False)
    name = fields.Char(translate=True, track_visibility='onchange')
    age = fields.Integer(copy=False)
    ethnic_group = fields.Many2one('ethnic.groups')
    gender = fields.Selection(selection=[('Male', 'M'), ('Female', 'F')])
    address = fields.Many2one('res.country.state', domain="[('country_id', '=', 69)]", track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    education_level = fields.Many2one('res.edlevel')
    field_of_study_id = fields.Many2many('field.study')
    gov_responsibility = fields.Char(string="Government Responsibility", translate=True, copy=False)
    work_place = fields.Char(translate=True, copy=False, track_visibility='onchange')
    position = fields.Char(translate=True, copy=False, track_visibility='onchange')
    start_of_support = fields.Selection(selection=[(str(num), num) for num in range(1900, (datetime.now().year)+1 )], string='Supporter Start Year')
    status = fields.Selection(selection=[('local', 'Local'), ('foreign', 'Foreign')], default='local', track_visibility='onchange')   
    email = fields.Char()
    website = fields.Char()
    active = fields.Boolean(default=True, track_visibility='onchange')
    reason = fields.Text(translate=True)

    @api.onchange('type_of_supporter')
    def _make_company(self):
        """This function will reject candate creation"""
        for record in self:
            if record.type_of_supporter == "company":
                record.is_company = True
            else:
                record.is_company = False

    @api.onchange('age')
    def _all_must_be_more_than_15(self):
        """This function will check if the age of the supporter is above 15"""
        for record in self:
            if record.age:
                if record.age < 15:
                    raise UserError(_("The Supporter's Age Must Be Above 15"))


    def archive_record(self):
        """This function will create wizard and archive a record"""
        wizard = self.env['archive.donor.wizard'].create({
            'reason': self.reason
        })
        return {
            'name': _('Archive Members Wizard'),
            'type': 'ir.actions.act_window',
            'res_model': 'archive.donor.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new'
        }

    def un_archive_record(self):
        """This function will unarchive a record"""
        for record in self:
            record.active = True