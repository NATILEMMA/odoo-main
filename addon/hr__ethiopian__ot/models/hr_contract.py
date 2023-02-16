from odoo import models, fields


class Contract(models.Model):
    _inherit = 'hr.contract'

    def _compute_wage(self):

        for recd in self:
            wage = recd.wage
            recd.over_hour = (wage/26)/8
    over_hour = fields.Float('Hour Wage', compute='_compute_wage')
