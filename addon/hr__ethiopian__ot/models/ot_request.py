import math
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,timedelta,date


class HROvertimeRequest(models.Model):
    _name = 'hr_ethiopian_ot.request'
    _description = "HR Overtime"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    def _get_employee_domain(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        domain = [('id', '=', employee.id)]
        if self.env.user.has_group('hr.group_hr_user'):
            domain = []
        return domain

    name = fields.Char('Name', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  domain=_get_employee_domain, default=lambda self: self.env.user.employee_id.id,
                                  required=True)
    hr_payslip = fields.Many2one('hr.payslip', string='payslip')

    contract_id = fields.Many2one('hr.contract', string="Contract",
                                  related="employee_id.contract_id",
                                  )
    department_id = fields.Many2one('hr.department', string="Department",
                                    related="employee_id.department_id")
    job_id = fields.Many2one('hr.job', string="Job", related="employee_id.job_id")
    manager_id = fields.Many2one('res.users', string="Manager",
                                 related="employee_id.parent_id.user_id", store=True)
    state = fields.Selection([
                              ('Pre_draft', 'Draft'),
                              ('draft', 'Checked'),
                              ('f_approve', 'Waiting'),
                              ('approved', 'Approved'),
                              ('calculated', 'Calculated'),
                              ('refused', 'Refused'),
                              ('paid', 'Paid')], string="State",
                             default="Pre_draft", tracking=True)
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date to')
    ot_times = fields.One2many('hr_ethiopian_ot.times', 'request_id')
    current_user = fields.Many2one('res.users', string="Current User",
                                   related='employee_id.user_id',
                                   default=lambda self: self.env.uid,
                                   store=True)
    company_id = fields.Many2one('res.company', 'Company', index=True,
                                 default=lambda self: self.env.company)
    payslip_paid = fields.Boolean('Paid in Payslip', readonly=True)
    total = fields.Float('Total', digits=(12, 2))

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    def calculate(self):

        clause_final = [('id', '=', self.contract_id.id)]
        search_results = self.env['hr.contract'].search(clause_final).ids
        if search_results:
            for search_result in self.env['hr.contract'].browse(search_results):
                payment_per_hour = search_result.over_hour
            total = 0.0
            clause_final_times = [('request_id', '=', self.id)]
            search_results_times = self.env['hr_ethiopian_ot.times'].search(clause_final_times).ids
            if search_results_times:
                for search_results_time in self.env['hr_ethiopian_ot.times'].browse(search_results_times):
                    payment_total = payment_per_hour * search_results_time.rate_amount * search_results_time.worked_hour
                    total = total + payment_total
                    search_results_time.write({'payment_total':payment_total,'payment_per_hour':payment_per_hour})
                self.write({"total":total, "state":"calculated"})
        else:
            raise ValidationError('The selected employee has no contract')

    @api.model
    def create(self, values):

        request_id = super(HROvertimeRequest, self.sudo()).create(values)
        date_from = fields.Date.from_string(values['date_from'])
        date_to = fields.Date.from_string(values['date_to'])
        delta = timedelta(days=1)
        while date_from <= date_to:
            ot_times = {
                'date_from': date_from,
                'date_name': date_from.strftime('%A'),
                'request_id': request_id.id
            }
            holiday = self.env['hr_ethiopian_ot.times'].create(ot_times)

            date_from += delta
        return request_id

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for req in self:
            domain = [
                ('date_from', '<=', req.date_to),
                ('date_to', '>=', req.date_from),
                ('employee_id', '=', req.employee_id.id),
                ('id', '!=', req.id),
                ('state', 'not in', ['refused']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_(
                    'You can not have 2 Overtime requests that overlaps on same day!'))

    def cheak(self):
     if self.date_from and self.date_to:
       if self.date_from > self.date_to:
         raise ValidationError('Start Date must be less than End Date or the time must be less than 24')
       else:
         employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
         self.name= employee.name
         group = self.env.ref('account.group_account_invoice', False)
         return self.sudo().write({
            'state': 'draft'})

    def set_to_waiting(self):
        return self.sudo().write({
            'state': 'f_approve'})

    def submit_to_f(self):
        # notification to employee
        recipient_partners = [(4, self.current_user.partner_id.id)]
        body = "Your OverTime Request Waiting Finance Approve .."
        msg = _(body)
        group = self.env.ref('account.group_account_invoice', False)
        recipient_partners = []
        body = "You Get New Time in Lieu Request From Employee : " + str(
            self.employee_id.name)
        msg = _(body)
        return self.sudo().write({
            'state': 'f_approve'
        })

    def approve(self):
     
        # notification to employee :
        recipient_partners = [(4, self.current_user.partner_id.id)]
        body = "Your Time In Lieu Request Has been Approved ..."
        msg = _(body)
        tracking = "1"
        return self.sudo().write({
            'state': 'approved',

        })

    def return_to_draft(self):

       self.state = 'draft'

    def recheck(self):
       self.state = 'f_approve'

    def reject(self):
       self.state = 'refused'


class HROvertimes(models.Model):
    _name = 'hr_ethiopian_ot.times'
    _description = 'Overtime works based on Ethiopian rule'

    date_from = fields.Date('Date From', required=True)
    start_time = fields.Float(string='overtime Start Time')
    end_time = fields.Float(string='OT End Time')
    start_time = fields.Float(string='OT StartTime')
    user_start_time = fields.Float(string='Req StartTime', store=True)
    user_end_time = fields.Float(string='Req EndTime', store=True)
    request_id = fields.Many2one('hr_ethiopian_ot.request', string="request Id")
    ot_id = fields.Many2one('hr_ethiopian_ot.rate', string="Rate ")

    ot_type = fields.Char(string='OT Type')
    rate_amount = fields.Float(string='OT Rate')
    payment_per_hour = fields.Float(string='Payment/Hour')
    payment_total = fields.Float(string='Total')
    worked_hour = fields.Float(string="Worked Hour", compute='_compute_days')
    payment = fields.Float(string="Calculated Payment")
    date_name = fields.Char(string='Date name')

    def _compute_days(self):
        
        for recd in self:
            if recd.start_time> 0 and recd.end_time> 0:
                if recd.start_time < recd.end_time:
                    recd.worked_hour = recd.end_time - recd.start_time
                    recd.user_end_time = recd.user_end_time
                    recd.user_start_time = recd.user_start_time
            else:
                recd.worked_hour= 0.0
                recd.user_end_time = recd.user_end_time
                recd.user_start_time = recd.user_start_time

    def float_to_time(float_hour):
        if float_hour == 24.0:
            return datetime.time.max
        return datetime.time(int(math.modf(float_hour)[1]), int(round(60 * math.modf(float_hour)[0], precision_digits=0)), 0)

    @api.onchange('worked_hour')
    def _onchange_worked_hour(self):
        for rec in self:
            date = rec.date_from
            day_name = date.strftime('%A')
            clause_final = [('employee_id', '=', self.request_id.employee_id.id),('state', '=', "open")]
            resource_calendar_id = self.env['hr.contract'].search(clause_final).resource_calendar_id
            clause_finalcalendar = [('calendar_id', '=', resource_calendar_id.id),("date_from", '<=' , date),("date_to",'>=' , date)]
            search_resultsresource_calendar_id = self.env['resource.calendar.leaves'].search(clause_finalcalendar).ids
            if search_resultsresource_calendar_id:
                clause_final = [('type', '=', 'holiday')]
                search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final).ids
                if search_results:
                    for search_result in self.env['hr_ethiopian_ot.rate'].browse(search_results):
                        rec.ot_id = search_result.id
                        rec.ot_type = search_result.type
                        rec.rate_amount = search_result.rate

                    return
            elif day_name == "Sunday":
                clause_final = [('type', '=', 'sunday')]
                search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final).ids
                if search_results:
                    for search_result in self.env['hr_ethiopian_ot.rate'].browse(search_results):
                        
                        rec.ot_id = search_result.id
                        rec.ot_type = search_result.type
                        rec.rate_amount = search_result.rate
                        rec.user_end_time = self.user_end_time
                        rec.user_start_time = self.user_start_time
            else:
                clause_final = [('type', '=', 'normal')]
                search_results = self.env['hr_ethiopian_ot.rate'].search(clause_final).ids
                if search_results:
                    if rec.start_time < rec.end_time:
                      for search_result in self.env['hr_ethiopian_ot.rate'].browse(search_results):
                        if search_result.start_time <= rec.start_time < search_result.end_time:
                            if search_result.start_time <= rec.end_time < search_result.end_time:
                                rec.ot_id = search_result.id
                                rec.ot_type = search_result.type
                                rec.rate_amount = search_result.rate
                                rec.user_end_time = self.user_end_time
                                rec.user_start_time = self.user_start_time
                                return
                            else:
                                rec.end_time = search_result.end_time
                                rec.ot_id = search_result.id
                                rec.ot_type = search_result.type
                                rec.rate_amount = search_result.rate
                                rec.user_end_time = self.user_end_time
                                rec.user_start_time = self.user_start_time
                                return
                        else:
                          if search_result.start_time <= rec.end_time < search_result.end_time:
                           rec.start_time = search_result.start_time
                           rec.ot_id = search_result.id
                           rec.ot_type = search_result.type
                           rec.rate_amount = search_result.rate
                           rec.user_end_time = self.user_end_time
                           rec.user_start_time = self.user_start_time
                           return
                    else:
                        raise ValidationError('The time is out of overtime range')

    @api.onchange('start_time', 'end_time')
    def _onchange_days(self):

        for recd in self:

            if recd.start_time and recd.end_time:
                if recd.start_time < recd.end_time < 24:
                    recd.worked_hour = recd.end_time - recd.start_time
                    recd.user_end_time = recd.end_time
                    recd.user_start_time = recd.start_time

                else:
                    raise ValidationError('Start Time must be less than End Time or the time must be less than 24')

