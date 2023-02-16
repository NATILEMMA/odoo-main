# -*- coding: utf-8 -*-

from odoo import models, fields, api


class membership_attachment(models.Model):
    _name = 'membership_attachment.membership_attachment'
    _description = 'membership_attachment.membership_attachment'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100
