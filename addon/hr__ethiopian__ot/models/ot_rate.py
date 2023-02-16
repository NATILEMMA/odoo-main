# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HROvertimeRate(models.Model):
    _name = 'hr_ethiopian_ot.rate'
    _description = 'Overtime works based on Ethiopian rule'

    name = fields.Char()
    type = fields.Selection([('normal', 'Normal'),
                              ('holiday', 'Holiday'),
                              ('sunday', 'Sunday')], string="Overtime Type", default="normal")
    rate = fields.Float(string='Rate')
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
