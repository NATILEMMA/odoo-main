"""This file will handle the changes on the attachemnt module"""


from odoo import fields, models



class AttachmentTypes(models.Model):
  _name="attachment.type"
  _description="This will handle the different types of attachments the member is allowed to attach"

  name = fields.Char(required=True, string="Attachment Type")


  _sql_constraints = [
                       ('Check on name', 'UNIQUE(name)', 'Each attachment type must be unique')
                     ]

class AttachmentModification(models.Model):
  _inherit="ir.attachment"

  attachment_type = fields.Many2one('attachment.type')
