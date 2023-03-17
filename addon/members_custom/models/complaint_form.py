"""This function will create a complain form"""


from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta,datetime
from ethiopian_date import EthiopianDateConverter
import logging
_logger = logging.getLogger(__name__)
dates = []
dd,mm,yy=0,0,0

class ComplaintCategory(models.Model):
  _name="complaint.category"
  _description="These will hold a list of categories for complaints"

  name = fields.Char(required=True)
  wereda_id = fields.Many2one('membership.handlers.branch', string="Department")
  responsible_person = fields.Many2one(related='wereda_id.complaint_handler', string="Responsible Person")

class Complaints(models.Model):
  _name="member.complaint"
  _description = 'This will contain the form for member complaint'
  _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

  subject = fields.Char(translate=True, track_visibility='onchange')
  victim_id = fields.Many2one('res.partner', domain="['|', '|', ('is_member', '=', True), ('is_league', '=', True), ('is_leader', '=', True)]")
  handler = fields.Many2one(related="victim_id.wereda_id.complaint_handler")
  perpertrators = fields.Many2many('res.partner', domain="['|', ('is_member', '=', True), ('is_leader', '=', True)]")
  circumstances= fields.Text(translate=True, track_visibility='onchange')
  conclusion_report = fields.Text(translate=True, track_visibility='onchange')
  state = fields.Selection(string="Complaint status", selection=[('new', 'New'), ('updated', 'Updated'), ('waiting for approval', 'Waiting For Approval'), ('resolved', 'Resolved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='new', track_visibility='onchange')
  handler = fields.Many2one(related="victim_id.wereda_id.complaint_handler")
  duration_of_remedy = fields.Integer(default=30, store=True, track_visibility='onchange')
  date_of_remedy = fields.Datetime(store=True, track_visibility='onchange')

  def send_pending_to_member(self):
      """This action will be able to send a pending complaint to a member"""
      mail_temp = self.env.ref('members_custom.complaint_waiting')
      for record in self:
        mail_temp.send_mail(record.id)
        record.state = 'waiting for approval'

  def send_review_to_member(self):
      """This action will be able to send a reviewed email to member"""
      mail_temp = self.env.ref('members_custom.complaint_review')
      for record in self:
        mail_temp.send_mail(record.id)

  def complaint_resolved(self):
      """This function will handle the state change when a resolved button is clicked"""
      if self.conclusion_report:
        self.state = 'resolved'
      else:
        raise UserError(_("Please fill in the conclusion report."))

  def complaint_rejected(self):
      """This function will handle the state change when rejected button is clicked"""
      if self.conclusion_report:
          self.state = 'rejected'
      else:
          raise UserError(_("Please fill in the conclusion report."))

  @api.depends('date_of_remedy')
  def _inverse_date_of_remedy(self):
      """This function will calculate the duration of remedy"""
      for record in self:
          if record.date_of_remedy:
              if record.date_of_remedy > record.create_date:
                days = (record.date_of_remedy - record.create_date).days
                record.duration_of_remedy = int(days)
              else:
                raise UserError(_('Pick A Date After The Date It Was Created'))

  @api.onchange('duration_of_remedy')
  def _compute_date_of_remedy(self):
      """This function will calculate the date of remedy"""
      for record in self:
          if record.duration_of_remedy:
              record.date_of_remedy = datetime.now() +  timedelta(days=record.duration_of_remedy)