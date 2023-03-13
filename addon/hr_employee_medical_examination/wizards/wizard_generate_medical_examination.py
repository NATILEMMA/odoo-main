# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import _, fields, models,api


class WizardGenerateMedicalExamination(models.TransientModel):

    _name = "wizard.generate.medical.examination"
    _description = "Generation wizard for medical examinations"

    name = fields.Char(required=True, string="Examination Name")
    year = fields.Char("Year", default=lambda r: str(date.today().year),)

    employee_ids = fields.Many2many(comodel_name="hr.employee", string="Employees")
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",)
    job_id = fields.Many2one(comodel_name="hr.job", string="Job",)

    instution_type_id = fields.Many2one("hr.employee.instution.type", string="Instution Type",)
    instution_id = fields.Many2one("res.partner", string="Instution",)
    examination_type_id = fields.Many2one("hr.employee.medical.examination.type", string="Examination Type",)


    @api.onchange('instution_type_id')
    def onchange_instution_type_id(self):
        for rec in self:
            return {'domain': {'instution_id': [('instution_type_id', '=', rec.instution_type_id.id)]}}
     
    

    def _prepare_employee_domain(self):
        res = []
        if self.job_id:
            res.append(("job_id", "=", self.job_id.id))
        if self.department_id:
            res.append(("department_id", "child_of", self.department_id.id))
        return res

    def populate(self):
        domain = self._prepare_employee_domain()
        employees = self.env["hr.employee"].search(domain)
        self.employee_ids = employees
        action = {
            "name": _("Generate Medical Examinations"),
            "type": "ir.actions.act_window",
            "res_model": "wizard.generate.medical.examination",
            "view_mode": "form",
            "target": "new",
            "res_id": self.id,
            "context": self._context,
        }
        return action

    def _create_examination_vals(self, employee):
        return {
            "name": _("%s on %s") % (self.name, employee.name),
            "employee_id": employee.id,
            "year": self.year,
            "instution_type_id":self.instution_type_id.id,
            "instution_id":self.instution_id.id,
            "examination_type_id":self.examination_type_id.id,
        }

    def create_medical_examinations(self):
        exams = self.env["hr.employee.medical.examination"]
        for form in self:
            for employee in form.employee_ids:
                exams |= self.env["hr.employee.medical.examination"].create(
                    form._create_examination_vals(employee)
                )
        action = self.env.ref(
            "hr_employee_medical_examination.hr_employee"
            "_medical_examination_act_window",
            False,
        )
        result = action.read()[0]
        result["domain"] = [("id", "in", exams.ids)]
        return result
