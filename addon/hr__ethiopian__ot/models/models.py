from odoo import models, fields, api


class hr__ethiopian__ot(models.Model):
    _name = 'hr__ethiopian__ot.hr__ethiopian__ot'
    _description = 'hr__ethiopian__ot.hr__ethiopian__ot'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100
