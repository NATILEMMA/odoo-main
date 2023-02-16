"""This file will compute the wage of different job titles"""

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, date


class GratuityExpenseGeneration(models.Model):
    _inherit = "hr.gratuity"


    def create_expense(self):
        """This function will create an expense based on gratuity"""
        for record in self:
            gratuity_id = self.env['product.product'].search([('name', '=', 'Gratuity'), ('default_code', '=', 'GRTEXP_101')])
            if record.corrected_employee_gratuity_amount != 0.00:
                self.env['hr.expense'].sudo().create({
                    'name': record.employee_id.name + "'s Gratituty Expense",
                    'product_id': gratuity_id.id,
                    'unit_amount': record.corrected_employee_gratuity_amount,
                    'quantity': 1,
                    'date': date.today(),
                    'employee_id': record.employee_id.id,
                    'gratuity_id': record.id
                })
                record.state = 'expensed'
            else:
                self.env['hr.expense'].sudo().create({
                    'name': record.employee_id.name + "'s Gratituty Expense",
                    'product_id': gratuity_id.id,
                    'unit_amount': record.employee_gratuity_amount,
                    'quantity': 1,
                    'date': date.today(),
                    'employee_id': record.employee_id.id,
                    'gratuity_id': record.id
                })
                record.state = 'expensed'



class GratuityExpenseInheritance(models.Model):
    _inherit = "hr.expense"

    gratuity_id = fields.Many2one('hr.gratuity', readonly=True, string="Gratuity")