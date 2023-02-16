from datetime import datetime
from odoo import models, fields, api, _


class AppointmentStack(models.Model):
    _name='lawsuit.appointment_stack'
    _description='law suit appointments history handler'
    
    law_suit_id = fields.Many2one('hr.lawsuit', 'Law Suit', help="field of related law suit")
    hearing_date = fields.Date(string="Hearing Date",help="Up comming hearing date")
    