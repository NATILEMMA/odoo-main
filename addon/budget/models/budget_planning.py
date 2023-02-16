import logging
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tokenize import group
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import os
from odoo.exceptions import UserError, Warning, ValidationError
import re
import base64
import requests
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)


STATES = [
    ('draft', 'Draft'),
    ('requested', 'Requested'),
    ('dep_approved', 'To be approve'),
    ('fin_approved', 'Approved'),
    ('ceo_approved', 'CEO Approved'),
    ('rejected', 'Rejected'),
    ('done', 'Done'), 
]
BudgetMethods = [
    ('incremental_budgeting','Incremental budgeting'),
    ('activity_based_budgeting','Activity-based budgeting'),
    ('value_proposition_budgeting','Value proposition budgeting'),
    ('zero_based_budgeting','Zero based budgeting'),
]

BudgeType = [
    ('monthly','Monthly'),
    ('quarterly','Quarterly'),
    ('semi','Semi'),
    ('annual','Annual'),


]
# class Project(models.Model):
#     _inherit = "project.project"

#     budget_account = fields.Many2one('budget.budget', 'Budget Account')


class BudgetPlanning(models.Model):
    _name = "budget.planning"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Budget Planning"
    
    
    name = fields.Char('Budget Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    # detail_information = fields.One2many(
    #     "budget.planning.details",
    #     "budget_id",
    #     help="Budget Planning detail Information",
    # )
    budget_methods = fields.Selection(BudgetMethods,
                              'Budget Methods', required=True,
                              copy=False,tracking=True)
    budget_type = fields.Many2one('budget.type', string="Budget Type")
    
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal Year")
    attchement_information = fields.One2many(
        "budget.planning.attachement",
        "budget_attachement_id",
        help="Budget Planning Document Attachement detail Information",
    )
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State',
        copy=False, default='normal', required=True)
    description = fields.Html(string='Description')
    planned_amount = fields.Float("Planned Amount",readonly=True )
    budgeted_amount = fields.Float("Budgeted Amount",tracking=True , readonly=True, store=True)
   
    amount_total = fields.Float('Total Planned Amount', readonly=True ,tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", string="Currency", readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account", copy=False, ondelete='set null',
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", check_company=True,
        help="Analytic account to which this project is linked for financial management. "
             "Use an analytic account to record cost and revenue on your project.",tracking=True)
    output = fields.Text('Out Put', translate=True)
    budget_planner = fields.Many2one('res.users',"Project Leader",tracking=True)
    employee_id = fields.Many2one('hr.employee', string="employee")
    state = fields.Selection(STATES,
                              'Status', required=True,
                              copy=False, default='draft',tracking=True)
    teams = fields.Many2many('hr.employee', string='Team Members' ,tracking=True)
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_attachment_number')
    date = fields.Datetime(string="Date")
    is_project = fields.Boolean(string="Integrate to Project", default=False)
    partner_id = fields.Many2many('res.partner', string='partner', tracking=True)
    partner_phone = fields.Char(related='partner_id.phone', related_sudo=False, tracking=True)
    partner_email = fields.Char(related='partner_id.email', related_sudo=False, tracking=True)
    alias_enabled = fields.Boolean(string='Use email alias', readonly=False)
    user_id = fields.Many2one('res.users', string='Budget Planner', default=lambda self: self.env.user, tracking=True)
    squ = fields.Char(string='BPF', required=True, copy=False, readonly=True,
                       default=lambda self: _('New'))
  
    work_stream_line = fields.One2many(
        "work.activity.stream",
        "activity_id",
        help="Work stream budget breakdown",tracking=True
    )
    compute_field = fields.Boolean(string="check field", compute='get_user')
    attachment_amount = fields.Integer(compute="_count_attachments",tracking=True)
    # attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    # attachment_count = fields.Integer(compute="_count_files")
    
    # def _count_files(self):
    #     """This function will count the number of attachments"""


    #     for record in self:
    #         attachments = self.env['ir.attachment'].search([('res_id', '=', record.id)])
    #         if attachments:
    #             record.attachment_count = len(attachments.mapped('type'))
    #         else:
    #             record.attachment_count = 0


  
    def _count_attachments(self):
        """This function will count the number of attachments"""
        obj_attachment = self.env['budget.planning.attachement']

        for rec in self:
            # attachment = obj_attachment.search([('budget_attachement_id','=',rec.id)])
            # _logger.info("@@@@@@@ %s",attachment)
            # for record in attachment:
            #     _logger.info("Loop %s",record.id)
            #     _logger.info("Loop %s",record.budget_attachment_ids)

            #     # attachments = self.env['ir.attachment'].search([('res_id', '=', record.budget_attachment_ids)])
            #     if record.budget_attachment_ids:
            #         rec.attachment_amount = len(record.budget_attachment_ids)
            #     else:
            #         rec.attachment_amount = 0
            rec.attachment_amount = obj_attachment.search_count([('budget_attachement_id','=',rec.id)])


    def action_project(self):
        action = self.env.ref('project.project_task_action_sub_task').read()[0]

        # only display subtasks of current task
        action['domain'] = [('id', 'child_of', self.id), ('id', '!=', self.id)]

        # update context, with all default values as 'quick_create' does not contains all field in its view
        if self._context.get('default_project_id'):
            default_project = self.env['project.project'].browse(self.env.context['default_project_id'])
        else:
            default_project = self.project_id.subtask_project_id or self.project_id
        ctx = dict(self.env.context)
        ctx.update({
            'default_name': self.env.context.get('name', self.name) + ':',
            'default_parent_id': self.id,  # will give default subtask field in `default_get`
            'default_company_id': default_project.company_id.id if default_project else self.env.company.id,
            'search_default_parent_id': self.id,
        })
        parent_values = self._subtask_values_from_parent(self.id)
        for fname, value in parent_values.items():
            if 'default_' + fname not in ctx:
                ctx['default_' + fname] = value
        action['context'] = ctx

        return action

    def action_get_attachment(self):
        pdf = self.env.ref('budget.planning.report_id').render_qweb_pdf(self.ids)
        b64_pdf = base64.b64encode(pdf[0])
        # save pdf as attachment
        name = "My Attachment"
        return self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'datas': b64_pdf,
            'datas_fname': name + '.pdf',
            'store_fname': name,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/x-pdf'
        })
        
   
    @api.onchange('is_project')
    def _onchange_on_project(self):
        _logger.info("###########intergatewithproject#############")
        _logger.info("Is Project:%s",self.is_project)
        if self.is_project is True:
            project_name = self.name
            # search_project = self.env["project.project"].sudo().search([('name','=',project_name)],limit=1)
            # _logger.info(search_project)
            # if len(search_project) > 0:
            #     _logger.info("Project XXXXXXXXXXXXXXXexis")
            # else:

            #     for line in self.work_stream_line:
            #         _logger.info("$$$$$ %s:",line.analytic_account_id.name)

            #         create_project = self.env['project.project'].create({
            #             "name": self.name,
            #             "analytic_account_id":line.analytic_account_id.id,
            #             "user_id": self.budget_planner.id,
            #         })
            #         self.env["project.task"].sudo().create({
            #                             "name": line.name,
            #                             "stage_id": 1,
            #                             "project_id":create_project.id,
            #                             "user_id":self.budget_planner.id,
                                    
            #                         })

            analytic_account = self.name
            search_project = self.env["project.project"].sudo().search([('name','=',project_name)],limit=1)
            budget = self.env['budget.planning'].search([('id','=',self.ids)],limit=1)
            _logger.info("work_stream_line:%s",budget.work_stream_line[0].analytic_account_id.id)
            if len(search_project) < 1:

                search_analytic_account = self.env['account.analytic.account'].search([('id','=',budget.work_stream_line[0].analytic_account_id.id)], limit=1)
                if len(search_analytic_account) < 1:
                    create_analytic_account = self.env["account.analytic.account"].sudo().create({"name": analytic_account,})
                    for line in budget.work_stream_line:   
                        project_id = self.env["project.project"].sudo().create({
                            "name": self.name,
                            "analytic_account_id":line.analytic_account_id.id,
                            "user_id": self.budget_planner.id,
                        })
                        break
                    self.is_project = True
                    for line in budget.work_stream_line:
                    
                        self.env["project.task"].sudo().create({
                                "name": line.name,
                                "stage_id": 1,
                                "project_id":project_id.id,
                                "user_id":self.budget_planner.id,
                                # "budget_amount":workstream.budget_amount,
                                # "target_area":workstream.target_point
                            })
                    # budget = self.env['budget.budget'].search([('id','=',create_analytic_account.name)])
                    # _logger.info(budget.id)
                    # if budget.budget_line:
                    #     val ={}
                    #     for line2 in budget.budget_line:
                    #         _logger.info("###########lin222222222")
                    #         _logger.info(line2)
                    #         val['budget_id'] = budget.id
                    #         val['planned_amount'] = line2.planned_amount
                    #         val['date_from'] = line2.date_from
                    #         val['date_to'] = line2.date_to
                    #         _logger.info("Val:%s",val)
                    #         budget_lines = create_analytic_account.budget_line.sudo().create(val)
                    #         _logger.info("budgetLINE:%s",budget_lines)
                else:
                    for line in budget.work_stream_line:   
                        project_id = self.env["project.project"].sudo().create({
                            "name": self.name,
                            "analytic_account_id":line.analytic_account_id.id,
                            "user_id": self.budget_planner.id,
                        })
                        break
                    self.is_project = True
                    for line in budget.work_stream_line:
                    
                        self.env["project.task"].sudo().create({
                                "name": line.name,
                                "stage_id": 1,
                                "project_id":project_id.id,
                                "user_id":self.budget_planner.id,
                                # "budget_amount":workstream.budget_amount,
                                # "target_area":workstream.target_point
                            })
            else:
                _logger.info("Project Already Exist")
                self.is_project = True
                raise Warning("This budget is already linked to the project.")
        else:
            _logger.info("Is Project:%s",self.is_project)



    

    
    @api.depends('compute_field')
    def get_user(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('budget_planning.group_requester') and not res_user.has_group('budget_planning.group_request_budget_approval'):
            self.compute_field = True
            
        else:
            self.compute_field = False

    
    # def write(self, vals):
    #     if vals.get('work_stream_line', None) is not None:
    #         _logger.info("#################%s",vals)
    #         work_stream = vals.get('work_stream_line') 
    #         budget = 0 
    #         new_budget = 0
    #         for work in work_stream:
    #             if work[2] != False:
    #                 self.env["work.activity.stream"].sudo().create({
    #                    "name": work[2]['name'],
    #                     "target_point":work[2]['target_point'],
    #                     "budget_amount": work[2]['budget_amount'],
    #                     "activity_id": self.id  })
    #         for workstream in self:
    #             for line in workstream.work_stream_line:
    #                 new_budget += line.budget_amount
    #         res = super(BudgetPlanning, self).write({'planned_amount': budget + new_budget })
    #         return res
       
       
    def _compute_attachment_number(self):
        domain = [('res_model', '=', 'budget.planning'), ('user_id', 'in', self.ids)]
        attachment_data = self.env['ir.attachment'].read_group(domain, ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for request in self:
            request.attachment_number = attachment.get(request.id, 0)
            
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window']._for_xml_id('base.action_attachment')
        res['domain'] = [('res_model', '=', 'budget.planning'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'budget.planning', 'default_res_id': self.id}
        return res
            

    @api.model
    def create(self, vals):
        if vals.get('squ', _('New')) == _('New'):
            vals['squ'] = self.env['ir.sequence'].next_by_code('budget.planning') or _('New')
        if vals.get('work_stream_line', None) is not None:
            work_stream = vals.get('work_stream_line') 
            budget = 0 
            for work in work_stream:
                budget += work[2]['budget_amount']
            vals.update({'planned_amount':budget})
        res = super(BudgetPlanning, self).create(vals)
        return res

    def action_set_to_draft(self):
        self.state = "draft"
        budget = self.env['budget.planning'].search([('id','=',self.ids)],limit=1)
        for budget_line in self.work_stream_line:
            _logger.info("#########Budget Line##############")
            analytic_account = self.env['account.analytic.account'].search([('id','=',budget_line[0].analytic_account_id.id)])
            _logger.info(analytic_account.id)
            analytic_account.write({
                'is_allowed': False
            })
            for v in budget.teams:
                members = self.env['hr.employee'].search([('id','=',v.id)])
                members.write({
                    "is_allowed": False,
                    'accountAnalytic': False
                })
        super(BudgetPlanning, self).write({'state':'draft'})
        
    
    def action_reject(self):
        self.state = "rejected"
        super(BudgetPlanning, self).write({'state':'rejected'})
        

    def action_request(self):
        self.state = "requested"

        super(BudgetPlanning, self).write({'state':'requested'})
    
    
 
    def action_ceo_approve(self):
        self.state = "ceo_approved"
        budget = self.env['budget.planning'].search([('id','=',self.ids)],limit=1)
        _logger.info(budget.teams)
        
        for budget_line in self.work_stream_line:
            _logger.info("#########Budget Line##############")
            analytic_account = self.env['account.analytic.account'].search([('id','=',budget_line[0].analytic_account_id.id)])
            _logger.info(analytic_account.id)
            analytic_account.write({
                'is_allowed': True
            })
            for v in budget.teams:
                members = self.env['hr.employee'].search([('id','=',v.id)])
                members.write({
                    "is_allowed": True,
                    'accountAnalytic': analytic_account.id
                })
        super(BudgetPlanning, self).write({'state':'ceo_approved','analytic_account_id': analytic_account.id})
        
    def action_finanical_approve(self):
        project_name = self.name
        analytic_account = self.name
        today = datetime.today()
        new_date = today + relativedelta(years=1)
        search_project = self.env["project.project"].sudo().search([('name','=',project_name)])
       
        if len(search_project) > 0:
            _logger.info("Project Name already exist***************")
            budget = self.env["budget.budget"].sudo().search([('name','=',project_name)])

            if len(budget) >=1:
                _logger.info("Analytic account exist:--")
            else: 
                _logger.info("CREEEEEEEEEEEEEEEE")
                _logger.info(self.work_stream_line)
                budget = self.env["budget.budget"].sudo().create({
                    "name": project_name,
                    "date_from": today,
                    "date_to": new_date
                
                })
                _logger.info("budget:%s",budget)

                for budget_line in self.work_stream_line:
                    _logger.info("#########Budget Line##############")
                    vals = []
                    val = {}
                    analytic_account = self.env['account.analytic.account'].search([('id','=',budget_line.analytic_account_id.id)])
                    _logger.info(analytic_account.id)
                    # if budget_line.analytic_account_id.budget_line:
                    #         for line2 in analytic_account.budget_line:
                    #             _logger.info("###########lin222222222")
                    #             _logger.info(line2)
                    #             val['budget_id'] = budget.id
                    #             val['general_budget_id'] = budget_line.general_budget_id.id
                    #             val['analytic_account_id']= budget_line.analytic_account_id.id
                    #             val['planned_amount'] = line2.planned_amount
                    #             val['date_from'] = line2.date_from
                    #             val['date_to'] = line2.date_to
                    #             _logger.info("Val:%s",val)
                    #             budget_lines = budget.budget_line.sudo().create(val)
                    #             _logger.info("budgetLINE:%s",budget_lines)
                    # else:
                    
                    val['budget_id'] = budget.id
                    val['general_budget_id'] = budget_line.general_budget_id.id
                    val['analytic_account_id']= budget_line.analytic_account_id.id
                    val['planned_amount']= budget_line.budget_amount
                    val['date_from'] = today
                    val['date_to'] = new_date
                    _logger.info("No Details:%s",val)
                    budget_lines = budget.budget_line.sudo().create(val)

                    search = self.env["project.project"].sudo().search([('name','=',project_name)])
                        # search.write({
                        #     'bud':
                        # })
                    _logger.info("budgetLINE:%s",budget_lines)
                    
                for budget_line in self.work_stream_line:
                    _logger.info("Removvvvvvvvvvvvvvvvvvvvv")
                    analytic_account = self.env['account.budget.post'].search([('id','=',budget_line.general_budget_id.id)])
                    _logger.info(analytic_account.name)
                    remove_budget = self.env['budget.budget'].search([('name','=',analytic_account.name)])
                    _logger.info(remove_budget.id)
                    removed = remove_budget.unlink()
                    _logger.info("remove     |||           account=%s",removed)
                    analytic_account = self.env['account.analytic.account'].search([('id','=',analytic_account.id)])
                    _logger.info(analytic_account.id)
                    
                _logger.info(vals)   
                self.state = "fin_approved"
            
                super(BudgetPlanning, self).write({'state':'fin_approved'})
        else:
            analytic = self.env["account.analytic.account"].sudo().search([('id','=',self.work_stream_line[0].analytic_account_id.id)])
            _logger.info(analytic.budget_line)
            if len(analytic.budget_line) > 0:
                
                _logger.info("analytic account exist:--")
                raise Warning("analytic account exist, please check accounts")
            
            else:
                
                
                budget = self.env["budget.budget"].sudo().search([('name','=',project_name)])
                if len(budget) >= 1:
                    _logger.info("analytic account exist:--")
                else:
                    months = 11   
                    _logger.info("CREEEEEEEEEEEEEEEE")
                    _logger.info(self.work_stream_line)

                    budget = self.env["budget.budget"].sudo().create({
                        "name": project_name,
                        "date_from": fields.Date.to_string(datetime.now()),
                        "date_to": fields.Date.to_string(datetime.now() + timedelta(months))
                    
                    })
                    _logger.info("budget:%s",budget)

                    for budget_line in self.work_stream_line:
                        _logger.info("#########Budget Line##############")
                        _logger.info(budget_line.analytic_account_id.name)
                        vals = []
                        val = {}
                        analytic_account = self.env['account.analytic.account'].search([('id','=',budget_line.analytic_account_id.id)])
                        _logger.info("AA:%s",analytic_account.id)
                        # if analytic_account.budget_line:
                        #         for line2 in analytic_account.budget_line:
                        #             _logger.info("###########lin222222222")
                        #             _logger.info(line2)
                        #             val['budget_id'] = budget.id
                        #             val['general_budget_id'] = budget_line.general_budget_id.id
                        #             val['analytic_account_id']= budget_line.analytic_account_id.id
                        #             val['planned_amount'] = line2.planned_amount
                        #             val['date_from'] = line2.date_from
                        #             val['date_to'] = line2.date_to
                        #             _logger.info("Val:%s",val)
                        #             budget_lines = budget.budget_line.sudo().create(val)
                        #             _logger.info("budgetLINE:%s",budget_lines)
                        # else:
                            
                        val['budget_id'] = budget.id    
                        val['general_budget_id'] = budget_line.general_budget_id.id
                        val['analytic_account_id']= budget_line.analytic_account_id.id
                        val['planned_amount']= budget_line.budget_amount
                        val['date_from'] = today
                        val['date_to'] = new_date
                        _logger.info("No Details:%s",val)
                        budget_lines = budget.budget_line.sudo().create(val)
                        _logger.info("budgetLINE:%s",budget_lines)
                
                    for budget_line in self.work_stream_line:
                        _logger.info("Removvvvvvvvvvvvvvvvvvvvv")
                        analytic_account = self.env['account.budget.post'].search([('id','=',budget_line.general_budget_id.id)])
                        _logger.info(analytic_account.name)
                        remove_budget = self.env['budget.budget'].search([('name','=',analytic_account.name)])
                        _logger.info(remove_budget.id)
                        removed = remove_budget.unlink()
                        _logger.info("remove     |||           account=%s",removed)
                        analytic_account = self.env['account.analytic.account'].search([('id','=',analytic_account.id)])
                        _logger.info(analytic_account.id)
                        

                    

                    _logger.info(vals)   
                    self.state = "fin_approved"
                
                super(BudgetPlanning, self).write({'state':'fin_approved'})
                
    def action_done(self):     
        # budget = self.env["budget.budget"].sudo().search([('name','=',project_name)])
     
        # if len(budget) == 1:
        #     days = 10 
        #     months = 11
        #     analytic = self.env["account.analytic.account"].sudo().search([('name','=',budget.name)])
        #     for line in budget:
        #         self.env['budget.lines'].sudo().create({
        #             'budget_id': line.id,
        #             'analytic_account_id' : analytic.id,
        #             'general_budget_id' : budget.id,
        #             'planned_amount': self.planned_amount,
        #             'date_from': fields.Date.today(),
        #             "date_to": fields.Date.to_string(datetime.now() + timedelta(months)),
        #             "paid_date": fields.Date.today(),
        #         })
        self.state = "done"
        super(BudgetPlanning, self).write({'state':'done'})
                
    def margin_action(self): 
        search_project = self.env["project.project"].sudo().search([('name','=',self.name)])   
        planned_budget = self.env['budget.planning'].sudo().search([('name','=',self.name)])
        
        if planned_budget.name == self.name and self.state == 'done':
            
            date_cal = date.today() + relativedelta(months=+2)
            work_stream =[]
            for line in planned_budget.work_stream_line:
                work_stream.append ((line.name))
                
                # search_project.env['project.task'].sudo().create({
                #     'name': line.name,
                # })
            # n = 0  
            # for task in work_stream:
            #     _logger.info("######################")
            #     _logger.info(task)
            #     # _logger.info(self.project_id)
            #     task_list = self.env['project.task'].sudo().search(['project_id','like',search_project.id])
            #     _logger.info(task_list)
            #     self.env['project.task'].sudo().create({
                    
            #         'name': task
            #     })
            #     _logger.info("************** %s:",search_project)
            #     n +=1

        
class BudgetType(models.Model):
    _name = "budget.type"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Budget Type'

    name = fields.Char('Name')
    date_from = fields.Date('Start Date', required=True)
    date_to = fields.Date('End Date', required=True)


    @api.model
    def create(self, vals):
        fiscal_year = self.env['fiscal.year'].search([('state','=','active')],limit=1)
        _logger.info(vals)
        if str(fiscal_year.date_from) <= vals['date_from'] < str(fiscal_year.date_to):
            if str(fiscal_year.date_from) < vals['date_to'] <= str(fiscal_year.date_to):
                pass
                # super(BudgetType, self).create(vals)
            else:
                raise Warning(" End Date are not appropriate  budget fiscal date")
        else:
            raise Warning("Start Date are not appropriate  budget fiscal date")




class WorkStreamActivity(models.Model):
    _name = "work.activity.stream"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Work Stream Activity'


    @api.depends('budget_amount')
    def _compute_total(self):
        """
        Compute the total budget amount of the Work activity.
        """
        amount_total = values = 0.0
        _logger.info("#######Compute the total budget##########")
        ids =str(self.activity_id.ids)[1:]
        ids = ids[:1]
        budget_id = self.env['budget.planning'].search([('id','=',ids)])
        _logger.info("Budget Planning:%s",budget_id)
        budget = 0 
        for line in budget_id.work_stream_line:
            _logger.info(line.budget_amount)
            _logger.info("current value : %s",line.budget_amount)
            
            budget += line.budget_amount
            _logger.info(budget)
        _logger.info(budget)
        budget_id.write({'planned_amount':budget})

    # def write(self,vals):
    #     """
    #     Compute the total budget amount of the Work activity.
    #     """
    #     amount_total = values = 0.0
    #     _logger.info("#######Write Compute the total budget##########")
    #     ids =str(self.activity_id.ids)[1:]
    #     ids = ids[:1]
    #     budget_id = self.env['budget.planning'].search([('id','=',ids)])
    #     _logger.info("Budget Planning:%s",budget_id)
    #     budget = 0 
    #     for line in budget_id.work_stream_line:
    #         _logger.info("current value : %s",self.budget_amount)
            
    #         budget += line.budget_amount
    #         _logger.info(budget)
    #     _logger.info(budget)
    #     budget_id.write({'planned_amount':budget})
    
    
    
    activity_id = fields.Many2one('budget.planning', string='WorkStreamActivity Reference',help='Relation field', ondelete='cascade', index=True, copy=False)
    
    name = fields.Char('Activity Name',  tracking=True, store=True)
    quantity = fields.Integer('Quantity')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',tracking=True, store=True)
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position',tracking=True, store=True)
    target_point = fields.Char('Target Area',  tracking=True, store=True)
    budget_amount = fields.Float('Plane amount',  tracking=True, store=True)
    amount_total = fields.Float('Total Planned Amount', compute="_compute_total",readonly=True,   tracking=True, store=True)
    
   
class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"
    
    budgeted_amount = fields.Float('Budgeted amount',  tracking=True)
    used_percentage = fields.Float(
    compute ='_compute_budget_percentage', string='Budget Usage',
    help = "Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.")
    unused_percentage = fields.Float(
    compute ='_compute_budget_percentage', string='Rest Budget',
    help="Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.")
   
    def _compute_budget_percentage(self):
        for line in self:
            if line.theoritical_amount != 0.00:
                line.percentage = float((line.practical_amount or 0.0) / line.theoritical_amount)
            else:
                line.percentage = 0.00
   


# class BudgetPlanningDetails(models.Model):
#     _name = "budget.planning.details"
#     _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
#     _description = 'Budget Planning Detail Information'
    
#     @api.depends('budget_amount')
#     def _compute_total(self):
#         """
#         Compute the total budget amount of the Work activity.
#         """
#         amount_total = values = 0.0
#         for order in self:
#             amount_total = values = 0.0
           
#             values += order.budget_amount
#             values.append((values))
#             # order.update({
                
#             #     'amount_total': values + amount_tax,
#             # })
    
#     name = fields.Char('Activity Name',  tracking=True)
#     target_point = fields.Char('Target Area',  tracking=True)
#     budget_amount = fields.Float('Planned amount', tracking=True)
#     amount_total = fields.Float('Total Planned Amount', readonly=True, compute='_compute_total', tracking=True)
#     budget_id = fields.Many2one('budget.planning', string='Budget Reference',help='Relation field', ondelete='cascade', index=True, copy=False)
    
class Task(models.Model):
    _inherit="project.task"
    
    target_area = fields.Char('Target Area')
    budget_amount = fields.Float('Plan Amount')


class AttachmentTypes(models.Model):
    _name="budget.attachment.type"
    _description="This will handle the different types of budget planning related attachments"

    name = fields.Char(required=True, string="Attachment Type")


    _sql_constraints = [
                       ('Check on name', 'UNIQUE(name)', 'Each attachment type must be unique')
                     ]

class AttachmentModification(models.Model):
    _inherit="ir.attachment"

    budget_planning_attachment_type = fields.Many2one('budget.attachment.type')
 

class BudgetPlanningAttachemnt(models.Model):
    _name = "budget.planning.attachement"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Budget Planning Detail Information'
    
    file_name = fields.Char(string="File Name" ,tracking=True , store=True)
    budget_attachment_ids = fields.Many2many('ir.attachment', string='Attachments', store=True)
    budget_attachement_id = fields.Many2one('budget.planning', string='Budget Reference',help='Relation field', ondelete='cascade', index=True, copy=False)
    