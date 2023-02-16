
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta,datetime
import logging
_logger = logging.getLogger(__name__)

STATE = [
    ('new', 'New'),
    ('waiting', 'Waiting '),
    ('approved', 'Checked'),
    ('canceled', 'Cancelled'),
]

class MembershipReport(models.Model):
    _name="report.report"
    _description="These will hold a list of membership report"

    user_id = fields.Many2one("res.partner","From")
    how_did_you_find = fields.Char("How did you find out about the Segar Scholarship project?")
    how_often_do_you = fields.Char("How often do you use or access the scholarship portal?")
    your_participation = fields.Char("What was your participation?")
    rate_your_level = fields.Char("Please rate your level of satisfaction with the project")
    how_do_you_evaluate = fields.Char("How do you evaluate the time you spent on this project?")
    suggestions = fields.Char("Do you have any suggestions to improve this activity?")

    seq = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                        default=lambda self: _('New'))
    state = fields.Selection(STATE, string='Status', store=True,tracking=True,default='new')
    checked_date = fields.Date('Date')
    responsible_person = fields.Many2many('res.users', string="Checked By")


    @api.model
    def create(self, vals):
        if vals.get('seq', _('New')) == _('New'):
            vals['seq'] = self.env['ir.sequence'].next_by_code('report.report') or _('New')
            res = super(MembershipReport, self).create(vals)
            return res


  
    def feed_back_resolved(self):
        today = datetime.today().strftime("%m-%d-%Y")
        if self.responsible_person: 
            self.state = 'resolved'
            self.checked_date = today
        else:
            raise UserError(_("Please fill in the responsible person for feedback view"))

  
    def feed_back_rejected(self):
        today = datetime.today().strftime("%m-%d-%Y")
        if self.responsible_person: 
            self.state = 'resolved'
            self.checked_date = today
        else:
            raise UserError(_("Please fill in the responsible person for feedback view"))


    def feedback_waiting(self):
        today = datetime.today().strftime("%m-%d-%Y")
        if self.responsible_person: 
            self.state = 'resolved'
            self.checked_date = today
        else:
            raise UserError(_("Please fill in the responsible person for feedback view"))
