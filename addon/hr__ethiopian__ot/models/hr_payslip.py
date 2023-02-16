from odoo import models, api, fields


class PayslipOverTime(models.Model):
    _inherit = 'hr.payslip'

    overtime_ids1 = fields.Many2many('hr_ethiopian_ot.request')
    overtime_line = fields.One2many('payslip.overtime', 'payslip', string="overtime")
    total_amount2 = fields.Float(string='Total overtime')

    @api.onchange('overtime_line')
    def onchange_overtime_line(self):
        amount = 0
        for overtime in self.overtime_line:
            amount += overtime.amount
        self.input_line_ids.write({"amount": amount})
        return

    def overtime(self):
        clause = [('employee_id', '=', self.employee_id.id), ('state', '=', 'calculated')]
        terms = []
        total_num = 0
        try:
            self.overtime_line.unlink()
            ot = self.env['hr_ethiopian_ot.request'].search(clause)
            for overtime_id in ot:
                total = overtime_id.mapped('total')
                if overtime_id:
                    self.overtime_ids1 = overtime_id
                    values = {'name_of_employee': self.employee_id.name, 'amount': total[0],
                              'start_time': str(overtime_id.date_from), 'end_time': str(overtime_id.date_to),
                              'overtime_id': overtime_id}
                    total_num += total[0]
                    terms.append((0, 0, values))
            self.update({"total_amount2": total_num})
            self.overtime_line = terms
        except:
            for overtime_id in self.env['hr_ethiopian_ot.request'].search(clause):
                total = overtime_id.mapped('total')
                if overtime_id:
                    self.overtime_ids1 = overtime_id
                    values = {'name_of_employee': self.employee_id.name, 'amount': total[0],
                              'start_time': str(overtime_id.date_from), 'end_time': str(overtime_id.date_to),
                              'overtime_id': overtime_id}
                    total_num += total[0]
                    terms.append((0, 0, values))
            self.update({"total_amount2": total_num})
            self.overtime_line = terms
        return

    @api.onchange('contract_id')
    def onchange_contract(self):
        contract = self.contract_id
        clause = [('employee_id', '=', self.employee_id.id), ('state', '=', 'calculated')]
        terms = []
        total_num = 0
        try:
            self.overtime_line.unlink()
            for overtime_id in self.env['hr_ethiopian_ot.request'].search(clause):
                    total = overtime_id.mapped('total')
                    if overtime_id:
                        self.overtime_ids1 = overtime_id
                        values = {'name_of_employee': self.employee_id.name, 'amount': total[0],
                                  'start_time': str(overtime_id.date_from), 'end_time': str(overtime_id.date_to),
                                  'overtime_id': overtime_id}
                        total_num += total[0]
                        terms.append((0, 0, values))
            self.update({"total_amount2": total_num})
            self.overtime_line = terms
        except:
            for overtime_id in self.env['hr_ethiopian_ot.request'].search(clause):
                total = overtime_id.mapped('total')
                if overtime_id:
                    self.overtime_ids1 = overtime_id
                    values = {'name_of_employee': self.employee_id.name, 'amount': total[0],
                              'start_time': str(overtime_id.date_from), 'end_time': str(overtime_id.date_to),
                              'overtime_id': overtime_id}
                    total_num += total[0]
                    terms.append((0, 0, values))
            self.update({"total_amount2": total_num})
            self.overtime_line = terms
        return

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """
        function used for writing overtime record in payslip
        input tree.

        """
        res = super(PayslipOverTime, self).get_inputs(contracts, date_to, date_from)
        contract = self.contract_id
        clause = [('employee_id', '=', self.employee_id.id), ('state', '=', 'calculated')]
        input_data = {}
        for overtime_id in self.env['hr_ethiopian_ot.request'].search(clause):
            total = overtime_id.mapped('total')
            tm1 = str(date_to)
            tm2 = str(date_from)
            if overtime_id:
                self.overtime_ids1 = overtime_id
                input_data = {
                        'name': contracts.employee_id.name,
                        'code': "OT",
                        'amount': self.total_amount2,
                        'contract_id': contracts.id,
                    }
            else:
                input_data = {
                        'name': contracts.employee_id.name,
                        'code': "OT",
                        'amount': self.total_amount2,
                        'contract_id': contracts.id,
                    }
        if input_data:
            res.append(input_data)
            self.write({'total_amount2': self.total_amount2})
        else:
            input_data = {
                'name': contracts.employee_id.name,
                'code': "OT",
                'amount': self.total_amount2,
                'contract_id': contracts.id,
            }
            res.append(input_data)
        lon_obj = self.env['hr.loan'].search([('employee_id', '=', contracts.employee_id.id), ('state', '=', 'approve')])
        for loan in lon_obj:
            for loan_line in loan.loan_lines:
                if date_from <= loan_line.date <= date_to and not loan_line.paid:
                    input_loan = {
                        'loan_line_id': loan_line.id,
                        'name': contracts.employee_id.name,
                        'code': "LO",
                        'amount': loan_line.amount,
                        'contract_id': contracts.id,
                     }
                    res.append(input_loan)
                else:
                    input_loan = {
                        'loan_line_id': loan_line.id,
                        'name': contracts.employee_id.name,
                        'code': "LO",
                        'amount': loan_line.amount,
                        'contract_id': contracts.id,
                     }
                    res.append(input_loan)
                    
        return res

    def action_payslip_done(self):
        """
        function used for marking paid overtime
        request.

        """
        for recd in self.overtime_line:
            clause = [('id', '=', int((recd.overtime_id).id))]
            for overtime_id in self.env['hr_ethiopian_ot.request'].search(clause):
                overtime_id.state = "paid"
                overtime_id.hr_payslip = self.id
        self.compute_sheet()
        return self.write({'state': 'done'
                           })


class PaySlipOvertime(models.Model):
    _name = 'payslip.overtime'
    _description = 'payslip over time field'

    payslip = fields.Many2one("hr.payslip", string='payslip line')
    name_of_employee = fields.Char(string="Employee")
    type = fields.Selection([('normal', 'Normal'),
                             ('holiday', 'Holiday'),
                             ('sunday', 'Sunday')], string="Overtime Type",
                            default="normal")

    amount = fields.Float(string='Amount', readonly=True)
    overtime_id = fields.Many2one("hr_ethiopian_ot.request", string='overtime id')
    start_time = fields.Char(string='Start Time')
    end_time = fields.Char(string='End Time')
    is_change = fields.Boolean(string="Is Change", default=False)
