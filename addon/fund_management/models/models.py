import logging
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tokenize import group
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError
import os
from odoo.exceptions import UserError, Warning, ValidationError
import re
import base64
import requests
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)

MONTH = [
        ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
        ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), 
        ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December'), ]
QUARTER = [
        ('1st', 'First Quartner'),
        ('2nd', 'Second Quarter'),
        ('3rd','Third Quarter'),
        ('4th', 'Fourth Quarter')
]
STATES = [
    ('draft', 'Not Paid'),
    ('paid', 'Paid'),
    ('submitted', 'Submitted To Manager'),
    ('to_allocate','Allocated'),
    ('allocated','Approved'),
    ('canceled', 'Cancel'),
    ('done', 'Done'),
]

class FundApplicationStage(models.Model):
    _name = 'fund.application.stage'
    _description = 'Apllication Stage'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _order = 'sequence, id'

    def _get_default_fund_ids(self):
        default_fund_ids = self.env.context.get('default_fund_ids')
        return [default_fund_ids] if default_fund_ids else None

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    fund_ids = fields.Many2many('fund.collection',string='Funds',
        default=_get_default_fund_ids)
    legend_blocked = fields.Char(
        'Red Kanban Label', default=lambda s: _('Blocked'), translate=True, required=True,
        help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label', default=lambda s: _('Ready for Next Stage'), translate=True, required=True,
        help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
        'Grey Kanban Label', default=lambda s: _('In Progress'), translate=True, required=True,
        help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=[('model', '=', 'project.task')],
        help="If set an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    rating_template_id = fields.Many2one(
        'mail.template',
        string='Rating Email Template',
        domain=[('model', '=', 'project.task')],
        help="If set and if the project's rating configuration is 'Rating when changing stage', then an email will be sent to the customer when the task reaches this step.")
    auto_validation_kanban_state = fields.Boolean('Automatic kanban status', default=False,
        help="Automatically modify the kanban state when the customer replies to the feedback for this stage.\n"
            " * A good feedback from the customer will update the kanban state to 'ready for the new stage' (green bullet).\n"
            " * A medium or a bad feedback will set the kanban state to 'blocked' (red bullet).\n")

    # def unlink(self):
    #     stages = self
    #     default_project_id = self.env.context.get('default_project_id')
    #     if default_project_id:
    #         shared_stages = self.filtered(lambda x: len(x.project_ids) > 1 and default_project_id in x.project_ids.ids)
    #         tasks = self.env['project.task'].with_context(active_test=False).search([('project_id', '=', default_project_id), ('stage_id', 'in', self.ids)])
    #         if shared_stages and not tasks:
    #             shared_stages.write({'project_ids': [(3, default_project_id)]})
    #             stages = self.filtered(lambda x: x not in shared_stages)
    #     return super(FundApplicationStage, stages).unlink()


class FundCollection(models.Model):
    _name = 'fund.collection'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    @api.model
    def year_selection(self):
        year = 2000 # replace 2000 with your a start year
        year_list = []
        while year != 2030: # replace 2030 with your end year
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        fund_id = self.env.context.get('default_fund_id')
        if not fund_id:
            return False
        return self.stage_find(fund_id, [('fold', '=', False)])
        

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for task in self:
            if task.kanban_state == 'normal':
                task.kanban_state_label = task.legend_normal
            elif task.kanban_state == 'blocked':
                task.kanban_state_label = task.legend_blocked
            else:
                task.kanban_state_label = task.legend_done

    # @api.model
    # def _read_group_stage_ids(self, stages, domain, order):
    #     search_domain = [('id', 'in', stages.ids)]
    #     if 'default_fund_id' in self.env.context:
    #         search_domain = ['|', ('fund_ids', '=', self.env.context['default_fund_id'])] + search_domain

    #     stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
    #     return stages.browse(stage_ids)

    funder_id = fields.Many2one('res.partner', 'Name', required=True)
    name = fields.Char('Name')
    description = fields.Html('Internal Note')
    month = fields.Selection(MONTH,
                          string='Month',default="January", store=True,)
    year = fields.Selection(
        year_selection,
        string="Year",
        default="2015", # as a default value it would be 2019)
    )
    quarter = fields.Selection(QUARTER,
                          string='Quarter', store=True,)
    allocate_id = fields.One2many(
        "allocate.fund.line",
        "fund_id",
        help="Work stream budget breakdown",tracking=True
    )
    user_id = fields.Many2one('hr.employee')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
    ], default='0', index=True, string="Priority")
    stage_id = fields.Many2one('fund.application.stage', string='Stage', ondelete='restrict', tracking=True, index=True,
        default=_get_default_stage_id,
        domain="[('fund_ids', '=', fund_id)]", copy=False)
    tag_ids = fields.Many2many('project.tags', string='Tags')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='Kanban State',
        copy=False, default='normal', required=True)
    kanban_state_label = fields.Char(compute='_compute_kanban_state_label', string='Kanban State Label', tracking=True)
    create_date = fields.Datetime("Created On", readonly=True, index=True)
    write_date = fields.Datetime("Last Updated On", readonly=True, index=True)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    date_assign = fields.Datetime(string='Assigning Date', index=True, copy=False, readonly=True)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, tracking=True)
    date_deadline_formatted = fields.Char()
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True, related_sudo=False)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True, related_sudo=False)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True, related_sudo=False)
    color = fields.Integer(string='Color Index')
    partner_id = fields.Many2one('res.partner',
        string='Customer',
        default=lambda self: self._get_default_partner(),
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    state = fields.Selection(STATES,
                              'Status', required=True,
                              copy=False, default='draft',tracking=True)

    amount= fields.Float('Amount Received', required=True)
    department_id = fields.Many2one('hr.department','Department')
    project_id = fields.Many2one('project.team','Project Team')
    application_team = fields.Many2one('application.team', 'Application Team')
    grant_type = fields.Many2one('grant.type','Grant Type')
    grant_motheds = fields.Many2one('grant.method','Grant Method')
    receiver_id = fields.Many2one('res.users', string='Reciever', default=lambda self: self.env.user, tracking=True)
    payment_date = fields.Date('Payment Date')
    email_from = fields.Char(string='Email', help="These people will receive email.", index=True)
    sequence = fields.Integer(string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of tasks.")
    
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    attachment_amount = fields.Integer(compute="_count_attachments",tracking=True)
    
    squ = fields.Char(string='FMS', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
  
    def _count_attachments(self):
        """This function will count the number of attachments"""
        for record in self:
            attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
            if attachments:
                record.attachment_amount = len(attachments.mapped('type'))
            else:
                record.attachment_amount = 0

    # @api.model
    # def create(self, vals):
    #     if vals.get('squ', _('New')) == _('New'):
    #         vals['squ'] = self.env['ir.sequence'].next_by_code('fund.collection') or _('New')

    #     res = super(FundCollection, self).create(vals)
    #     return res

    @api.model
    def _get_default_partner(self):
        if 'default_fund_id' in self.env.context:
            default_fund_id = self.env['fund.collection'].browse(self.env.context['default_fund_id'])
            return default_fund_id.exists().partner_id
 
    @api.model
    def create(self, vals):
        months = [('1', 'January'),('2', 'February'),('3', 'March'),('4', 'April'),('5', 'May'),('6', 'June'),('7', 'July'),('8', 'August'), ('9', 'September'),('10', 'October'), ('11', 'November'), ('12', 'December')]
        month_name = dict(months).get(vals.get('month'))
        vals['name'] = 'Fund - %s - %s' % (month_name, vals.get('year'))
        vals['squ'] = self.env['ir.sequence'].next_by_code('fund.collection') or _('New')
        
        res = super(FundCollection, self).create(vals)
        return res

    def action_fund_recieved(self):
        self.state = "paid"
        self.payment_date = datetime.today()
        super(FundCollection, self).write({'state':'paid'})

    def action_fund_manager_approval(self):
        self.state = "submitted"
        self.user_id = self.env.uid
        super(FundCollection, self).write({'state':'submitted','user_id': self.env.uid})

    def action_fund_allocation(self):
        _logger.info("############ action_fund_allocation")
        today = datetime.today()
        new_date = today + relativedelta(years=1)
        fund = self.env['fund.fund'].create({
            'name' : self.name, 
            "date_from": today,
            "date_to": new_date
        })
        
        for line in self.allocate_id:
                    _logger.info("#########Fund Line##############")
                    vals = []
                    val = {}
                    analytic_account = self.env['account.analytic.account'].search([('id','=',line.analytic_account_id.id)])
                    _logger.info(analytic_account.id)
                    if analytic_account.fund_line:
                            for line2 in analytic_account.fund_line:
                                _logger.info(line2)
                                val['fund_id'] = fund.id
                                val['general_fund_id'] = line.general_fund_id.id
                                val['fund_analytic_account_id']= line.analytic_account_id.id
                                val['planned_amount'] = line2.planned_amount
                                val['date_from'] = line2.date_from
                                val['date_to'] = line2.date_to
                                _logger.info("Val:%s",val)
                                fund_lines = fund.fund_line.sudo().create(val)
                                _logger.info("FundLINE:%s",fund_lines)
                                _logger.info(analytic_account.name)
                                remove = self.env['fund.fund'].search([('name','=',analytic_account.name)])
                                _logger.info(remove.id)
                                removed = remove.unlink()
                                _logger.info("remove     |||           account=%s",removed)
        
                    else:
                        val['fund_id'] = fund.id
                        val['general_fund_id'] = line.general_fund_id.id
                        val['fund_analytic_account_id']= line.analytic_account_id.id
                        val['planned_amount'] = line.amount
                        val['date_from'] = today#line2.date_from
                        val['date_to'] = new_date #line2.date_to
                        _logger.info("Val:%s",val)
                        fund_lines = fund.fund_line.sudo().create(val)
                        _logger.info("FundLINE:%s",fund_lines)
                        remove = self.env['fund.fund'].search([('name','=',analytic_account.name)])
                        _logger.info(remove.id)
                        removed = remove.unlink()
                        _logger.info("remove     |||           account=%s",removed)

        self.state = "to_allocate"

        super(FundCollection, self).write({'state':'to_allocate'})

    def action_fund_distribution(self):
        _logger.info("##################FUND")
        today = datetime.today()
        new_date = today + relativedelta(years=1)
        self.state = "draft"
        fund = self.env['fund.fund'].search([('id','in', self.ids)])
        _logger.info("FUND:%s",fund)
        # for line in self.allocate_id:
        #     _logger.info("line:%s",line)
        #     _logger.info("line:%s",line.analytic_account_id.name)
        #     analyticAccount = self.env['account.analytic.account'].search([('id','=',line.analytic_account_id.id)])
        #     _logger.info(analyticAccount.group_id.name)
        #     if len(analyticAccount) > 0 and analyticAccount.group_id.name == "Budget":
        #         _logger.info("###################")
        #         create_budget_fund = analyticAccount.fund_line.create({
        #             'fund_id': fund.ids,
        #             'general_fund_id': line.general_fund_id.id,
        #             'fund_analytic_account_id': line.analytic_account_id.id,
        #             "date_from": today,
        #             "date_to": new_date,
        #             'planned_amount': line.amount

        #         })
        #         _logger.info("Created:%s",create_budget_fund)
            
           

        super(FundCollection, self).write({'state':'draft'})

    def action_paid(self):
        if not self.receiver_id:
            raise Warning('Please select a Receiver of the fund\n Click Modify --> Select Receiver.')
        if not self.payment_date:
            raise Warning('Please select payment date of the fund\n Click Modify --> Select Payment Date.')
        
        res = self.write({'state':'paid'})
        if res:
            notify_user = self.notify_user()
            return res
        return 

    
    def action_submitted(self):
        if not self.receiver_id:
            raise Warning('Please select a Receiver of the fund\n Click Modify --> Select Receiver.')
        
        self.state = "submitted"
        super(FundCollection, self).write({'state':'submitted'})
       
    def action_set_to_draft(self):
        self.state = "draft"
        super(FundCollection, self).write({'state':'draft'})

    
    def action_reject(self):
        self.state = "rejected"
        super(FundCollection, self).write({'state':'rejected'})
        
    
    def notify_user(self):
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('bday_fund_mgmt', 'email_template_to_fund_submission')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
                
        return self.pool['mail.template'].send_mail(self.env.cr, self.env.uid, template_id, self.id, force_send=True,context=self.env.context)

        
class ProjectTeam(models.Model):
    _name = 'project.team'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    code = fields.Char('Code')
    name = fields.Char('Name')
    project_id = fields.Many2one('project.project', 'Projects')
    project_manager = fields.Many2one('hr.employee','Project Manager')
    # project_team = fields.Many2many('hr.employee', 'Project Members')

class ApplicationTeam(models.Model):
    _name = 'application.team'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    code = fields.Char('Code')
    name = fields.Char('Name')
    team_leader = fields.Many2one('hr.employee','Team Leader')
    # team_member = fields.Many2many('hr.employee', 'Team Members')

class GrantType(models.Model):
    _name = 'grant.type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    code = fields.Char('Code')
    name = fields.Char('Name')
   
class GrantMethods(models.Model):
    _name = 'grant.method'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin']

    code = fields.Char('Code')
    name = fields.Char('Name')
   

class Employee(models.Model):
    _inherit='hr.employee'

    is_fund_mgr = fields.Boolean('Is Fund Manager', default=False)


class Users(models.Model):
    _inherit='res.users'

    @api.model
    def create(self, vals):
        # import pdb;pdb.set_trace()
        user_id = super(Users, self).create(vals)
        employee_group_id = self.env['ir.model.data'].get_object_reference('base', 'group_user')[1]
        group_obj = self.env['ir.model.data'].get_object_reference('base', 'group_user')[0]
        group_id = self.env[group_obj].browse(employee_group_id)
        
        append_group = user_id.write({'groups_id': [(6, 0, [employee_group_id])]})

        employee = self.env['hr.employee'].create({
                'name':user_id.name,
                'work_email':user_id.login,
                'user_id':user_id.id,
            })
        return user_id

class AllocateToFundLine(models.Model):
    _name = "allocate.fund.line"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Allocate To Fund Line'


    fund_id = fields.Many2one('fund.collection', string='Reference', help='Relation field', ondelete='cascade', index=True, copy=False)
    amount = fields.Float("Amount")
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',tracking=True, store=True)
    general_fund_id = fields.Many2one('account.fund.post', 'Fund Position',tracking=True, store=True)
    
 

class Expense(models.Model):
    _name = 'fund.expense'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    _rec_name = 'purpose'

    funder_id = fields.Many2one('res.partner', 'Name')
    purpose = fields.Selection([('bday','Birthday Expense'), ('other','Other')], required=True)
    other_reason = fields.Text('Specify Other Reason')
    expense_amount = fields.Float('Expense Amount', required=True)
    spender = fields.Many2one('hr.employee','Expensed By', required=True, domain=[('is_fund_mgr','=',True)])
    payment_date = fields.Date('Payment Date', required=True)
    state = fields.Selection([
        ('draft', 'Not Expensed'),
        ('expense', 'Expensed'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    

    @api.model
    def action_expensed(self):
        return self.write({'state':'expense'})


