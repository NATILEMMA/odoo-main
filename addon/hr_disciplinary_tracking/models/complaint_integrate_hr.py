# This function will add complaint to employee and to user
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError,UserError

class EmployeeComplaints(models.Model):
    _name="employee.complaint"
    _description = 'This will contain the form for employee complaint'


    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default='New')
    subject = fields.Many2one('discipline.category', string="Subject", required=True)
    victim_id = fields.Many2one('res.users', default=lambda self: self.env.user, string="Victim", readonly=True)
    mode = fields.Selection(selection=[('by_employee', 'By Employee'), ('by_department', 'By Department'), ('by_company', 'By Company')], required=True)
    employee_offendors_ids = fields.Many2many('hr.employee', string="Employees")
    department_offendors_ids = fields.Many2many('hr.department', string="Departments")
    company_offendors_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    action = fields.Many2one('discipline.action', string="Action")
    action_details = fields.Text(string="Action Details")
    circumstances = fields.Text(string="Circumstances")
    state = fields.Selection(string="Complaint status", selection=[('new', 'New'), ('draft', 'Draft'), ('waiting for approval', 'Waiting For Approval'), ('resolved', 'Resolved')], default='new')
    disciplinary_id = fields.Many2one('disciplinary.action', string="Disciplinary Action")
    complaint_assessor = fields.Many2many('hr.employee', 'complaint_assessor_rel', 'emp_id', 'complaint_id', string="Complaint Assessors")

    @api.model
    def create(self, vals):
        """This function will create a complaint and save it as a draft"""
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.complaint')
        vals['state'] = 'draft'
        return super(EmployeeComplaints, self).create(vals)

    def in_progress(self):
        """This function will create a disciplinary action when button is clicked"""
        for complaint in self:
            if complaint.mode == 'by_employee':
                for employee in complaint.employee_offendors_ids:
                    self.disciplinary_id = self.env['disciplinary.action'].create({
                        'name': self.env['ir.sequence'].next_by_code('disciplinary.action'),
                        'employee_name': employee.id,
                        'department_name': employee.department_id.id,
                        'discipline_reason': complaint.subject.id,
                        'note': complaint.circumstances,
                        'joined_date': complaint.create_date,
                        'state': 'draft',
                        'complaint_id': complaint.id,
                    })
                    if self.disciplinary_id.action.name == 'Written Warning':
                        self.disciplinary_id.warning = 1
                    elif self.disciplinary_id.action.name == 'Suspend the Employee for one Week':
                        self.disciplinary_id.warning = 2
                    elif self.disciplinary_id.action.name == 'Terminate the Employee':
                        self.disciplinary_id.warning = 3
                    elif self.disciplinary_id.action.name == 'No Action':
                        self.disciplinary_id.warning = 4
                    else:
                        self.disciplinary_id.warning = 5
            elif complaint.mode == 'by_department':
                complaint.complaint_assessor = [(6, 0, complaint.department_offendors_ids.department_complaint_assessor.ids)]
            complaint.state = 'waiting for approval'

    def complaint_reviewed(self):
        """This function will change status after department reviewer is done"""
        for record in self:
            if not record.action:
                raise UserError(_('Please Fill In The Action To Be Taken And Detail Explanation'))
            elif not record.action_details:
                raise UserError(_('Please Fill In The Action To Be Taken And Detail Explanation'))
            record.state ='resolved'

class ResUsersComplaint(models.Model):
    _inherit = "res.users"

    employee_complaint_ids = fields.One2many('employee.complaint', 'victim_id')
    discipline_count = fields.Integer(compute="_compute_discipline_count")

    def _compute_discipline_count(self):
        """This function will count the number of actions for a user"""
        for record in self:
            employee = self.env['hr.employee'].search([('user_id', '=', record.id)])
            actions = self.env['disciplinary.action'].search([('state', 'in', ('explain','action')), ('employee_name', '=', employee.id)])
            record.discipline_count = len(actions)


class HrDepartmentComplaint(models.Model):
    _inherit = "hr.department"

    department_complaint_assessor = fields.Many2one('hr.employee', domain=lambda self: [("user_id.groups_id", "=", self.env.ref("hr.group_hr_manager").id)],
                                                                   string="Complaint Assessor")