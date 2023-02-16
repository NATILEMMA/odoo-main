# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class GratuityAccountingConfiguration(models.Model):
    _name = 'hr.gratuity.accounting.configuration'
    _rec_name = 'name'
    _description = "Gratuity Accounting Configuration"

    name = fields.Char()
    active = fields.Boolean(default=True)
    add_to_base = fields.Boolean(string="Add To The Basic Severance Pay?")
    gratuity_credit_account = fields.Many2one('account.account', help="Credit account for the gratuity")
    gratuity_debit_account = fields.Many2one('account.account', help="Debit account for the gratuity")
    gratuity_journal = fields.Many2one('account.journal', help="Journal for the gratuity")
    config_contract_type = fields.Selection(
        [('limited', 'Limited'),
         ('unlimited', 'Unlimited')], default="limited", required=True,
        string='Contract Type')
    gratuity_configuration_table = fields.One2many('gratuity.configuration',
                                                   'gratuity_accounting_configuration_id')


    _sql_constraints = [('name_uniq', 'unique(name)',
                         'Gratuity configuration name should be unique!')]


    @api.onchange('add_to_base')
    def _add_base_rule(self):
        """This function will add a base rule to any severance that will be add on total retirement"""
        for record in self:
            if record.add_to_base:
                base_severance = self.env['hr.gratuity.accounting.configuration'].search([('name', '=', 'Basic')])
                if base_severance and len(base_severance.gratuity_configuration_table) == 1:
                    rule = base_severance.gratuity_configuration_table
                    added_rule = self.env['gratuity.configuration'].sudo().create({
                        'gratuity_accounting_configuration_id': record.id,
                        'name': "Base " + rule.name,
                        'active': True,
                        'from_year': rule.from_year,
                        'to_year': rule.to_year,
                        'employee_daily_wage_days': rule.employee_daily_wage_days,
                        'employee_working_days': rule.employee_working_days,
                        'percentage': rule.percentage,
                        'company_id': rule.company_id.id
                    })
                    record.sudo().write({
                        'gratuity_configuration_table': [(
                            6,
                            0,
                            [added_rule.id]
                        )]
                    })
                else:
                    raise UserError(_("Please Add, To The Base Severance Named 'Basic', One Rule"))
            else:
                record.sudo().write({
                    'gratuity_configuration_table': [(5, 0, 0)]
                })
                    