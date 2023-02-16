from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, tools, _


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def check(self):
        res = super(HrPayslipRun, self).check()
        for slip_id in self.slip_ids:
          if slip_id:
            clause = [('employee_id', '=', slip_id.employee_id.id), ('state', '=', 'calculated')]
            terms = []
            total_num = 0
            if slip_id:
                slip_id.overtime_line.unlink()
            ot = self.env['hr_ethiopian_ot.request'].search(clause)
            if ot:
                for overtime_id in ot:
                    total = overtime_id.mapped('total')
                    if overtime_id:
                        slip_id.overtime_ids1 = overtime_id
                        values = {'name_of_employee': slip_id.employee_id.name, 'amount': total[0],
                                  'start_time': str(overtime_id.date_from), 'end_time': str(overtime_id.date_to),
                                  'overtime_id': overtime_id.id,'payslip':slip_id.id}
                        total_num += total[0]
                        terms.append((0, 0, values))
                slip_id.update({"total_amount2": total_num})
                slip_id.update({'overtime_line': terms})
                slip_id.input_line_ids.update({"amount": total_num})
          else:
             raise ValidationError(_('You have to select employee'))


        return res

    def post_to_journal(self):
        res = super(HrPayslipRun, self).post_to_journal()
        for slip_id in self.slip_ids:
            for recd in slip_id.overtime_line:
                clause = [('id', '=', int((recd.overtime_id).id))]
                for overtime_id in self.env['hr_ethiopian_ot.request'].search(clause):
                    overtime_id.state = "paid"
        return res

    def draft_payslip_run(self):
        res = super(HrPayslipRun, self).draft_payslip_run()
        for slip_id in self.slip_ids:
            for recd in slip_id.overtime_line:
                clause = [('id', '=', int((recd.overtime_id).id))]
                for overtime_id in self.env['hr_ethiopian_ot.request'].search(clause):
                    overtime_id.state = "calculated"
        return res