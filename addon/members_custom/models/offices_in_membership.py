"""This file will deal with the modification to be made on offices"""

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from ethiopian_date import EthiopianDateConverter

import logging
_logger = logging.getLogger(__name__)

dates = []
dd,mm,yy=0,0,0

class MainOffice(models.Model):
    _name="main.office"
    _description="This model will contain the main offices the cells bellong in"

    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).parent_id.id

    name = fields.Char(required=True, translate=True)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, copy=False, default=_default_subcity)
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda)
    main_type_id = fields.Char(translate=True)
    cell_ids = fields.One2many('member.cells', 'main_office', readonly=True, copy=False)
    total_cell = fields.Integer(compute="_calculate_cells")
    total_members = fields.Integer(compute="_calculate_cells")
    leader_ids = fields.Many2many('res.partner', copy=False)
    total_membership_fee = fields.Float(compute="_calculate_cells")
    date_of_meeting_eachother = fields.Date()
#    date_of_meeting_eachother_ethiopian = fields.Date(store=True)
    place_of_meeting_eachother = fields.Char(translate=True)
    time_of_meeting_eachother = fields.Float()
    date_of_meeting_cells = fields.Date()
#    date_of_meeting_cells_ethiopian = fields.Date(store=True)
    place_of_meeting_cells = fields.Char(translate=True)
    time_of_meeting_cells = fields.Float()
    meeting_memebers_every = fields.Integer()

    # @api.model
    # def date_convert_and_set(self,picked_date):
    #     _logger.info("##############################")
    #     _logger.info(picked_date)
    #     _logger.info(picked_date['current_model'])
    #     _logger.info(picked_date['url'])
    #     try:
    #         dd = picked_date['url'].split('id=')
    #         id = str(dd[1]).split('&')
    #         _logger.info("### ID:%s",id[0])
    #         m = picked_date['url'].split('model=')
    #         mm = m[1].split('&')
    #         _logger.info("###model:%s",mm[0])
    #         if len(id[0]) <= 0:
    #             _logger.info("################# not fund")

    #         else:
    #             # if len(picked_date['current_model']) > 6:
    #                 models = mm[0]
    #                 search = self.env[models].search([('id','=',id[0])])
    #                 _logger.info(search)
    #                 date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
    #                 date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
    #                 # date,time = str(datetime.now()).split(" ")
    #                 # date = str(date_et) + " " + str(f"{time}")
    #                 # date = str(f"{picked_date['year']}"+"-"+f"{picked_date['month']}"+"-"+f"{picked_date['day']}") + " " + str(f"{time}")
    #                 if models == "main.office":
    #                     if picked_date['pick'] == 1:
    #                         search.write({
    #                             'date_of_meeting_eachother': date_gr,
    #                             'date_of_meeting_eachother_ethiopian': date
    #                         })
    #                         return search
    #                     if picked_date['pick'] == 2:
    #                         search.write({
    #                             'date_of_meeting_cells': date_gr,
    #                             'date_of_meeting_cells_ethiopian': date
    #                         })
    #                         return search

    #     except:
    #         pass
    #     if picked_date['current_model'] is not None:
    #         # models = self.env[f"{picked_date['current_model']}"].search([])
    #         # _logger.info("Models:  %s  ",models)
    #         # to_ethiopian
    #         date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
    #         _logger.info("DATE%s",date_gr)

    #         _logger.info(datetime.now())
    #         date,time = str(datetime.now()).split(" ")
    #         _logger.info(str(date_gr) + " " + str(f"{time}"))
    #         dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']

    #         # date = str(date_et) + " " + str(f"{time}")
    #         date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)

    #         date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
    #         data = {
    #             'day':picked_date['day'],
    #             'month': picked_date['month'],
    #             'year': picked_date['year'],
    #             'pick': picked_date['pick']
    #         }
      
    #         dates.append(data)

    # @api.model
    # def create(self, vals):

    #     _logger.info("############# Create:%s",dates)
    #     for i in range(0, len(dates)):
  
    #         if i == (len(dates)-1):
    #             _logger.info("The last element of list using loop : "
    #                 + str(dates[i]))

    #             date1 = dates[i - 1]
    #             date2 = dates[i]


    #             gdate1 = EthiopianDateConverter.to_gregorian(date1['year'],date1['month'],date1['day'])
    #             gdate2 = EthiopianDateConverter.to_gregorian(date2['year'],date2['month'],date2['day'])

    #             edate1 = EthiopianDateConverter.to_ethiopian(gdate1.year,gdate1.month,gdate1.day)
    #             edate2 = EthiopianDateConverter.to_ethiopian(gdate2.year,gdate2.month,gdate2.day)

    #             vals['date_of_meeting_eachother'] = gdate1
    #             vals['date_of_meeting_eachother_ethiopian'] = edate1

    #             vals['date_of_meeting_cells'] = gdate2
    #             vals['date_of_meeting_cells_ethiopian'] = edate2

    #     try:
    #         if vals['date_of_meeting_eachother'] is not None or vals['date_of_meeting_cells'] is not None:
    #             date1 = vals['date_of_meeting_eachother']
    #             date2 = vals['date_of_meeting_cells']
    #             Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
    #             Edate2 = EthiopianDateConverter.to_ethiopian(date2.year,date2.month,date2.day)
    #             vals['date_of_meeting_eachother_ethiopian'] = Edate1
    #             vals['date_of_meeting_cells_ethiopian'] = Edate2
    #     except:
    #         pass
    #     _logger.info(vals)
    #     return super(MainOffice, self).create(vals)


    # def write(self, vals):
    #     try:
    #         if vals['date_of_meeting_eachother'] is not None:
    #             date_str = str(vals['date_of_meeting_eachother']).split(' ')[0]
    #             date_time_obj = date_str.split('-')
    #             Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
    #             vals['date_of_meeting_eachother_ethiopian'] = Edate
    #     except:
    #         pass
    #     try:
    #         if vals['date_of_meeting_cells'] is not None:
    #             date_str = str(vals['date_of_meeting_cells']).split(' ')[0]
    #             date_time_obj = date_str.split('-')
    #             Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
    #             vals['date_of_meeting_cells_ethiopian'] = Edate
    #     except:
    #         pass
    #     return super(MainOffice, self).write(vals) 

    @api.depends('cell_ids')
    def _calculate_cells(self):
        """This function will calculate the total cells of main_office"""
        for record in self:
            record.total_cell = len(record.cell_ids.ids)
            total = record.cell_ids.mapped('total')
            count = 0
            for memb in total:
                count += memb
            record.total_members = count            
            total_memb_fee = record.cell_ids.mapped('total_membership_fee')
            total_membership_fee = 0
            for i in total_memb_fee:
                total_membership_fee += i
            record.total_membership_fee = total_membership_fee
            record.leader_ids = record.cell_ids.mapped('leaders_ids').ids


class Cells(models.Model):
    _name="member.cells"
    _description="This model will contain the cells members will belong in"


    def _default_wereda(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).id

    def _default_subcity(self):
        """This function will set a default value to wereda"""
        return self.env['membership.handlers.branch'].search([('branch_manager', '=', self.env.user.id)], limit=1).parent_id.id

    name = fields.Char(required=True, translate=True)
    subcity_id = fields.Many2one('membership.handlers.parent', string="Subcity", required=True, copy=False, default=_default_subcity)
    wereda_id = fields.Many2one('membership.handlers.branch', string="Woreda", required=True, default=_default_wereda)
    main_office = fields.Many2one('main.office', domain="[('wereda_id', '=', wereda_id)]", required=True)
    cell_type_id = fields.Char(translate=True)
    members_ids = fields.Many2many('res.partner', domain="['&', '&', ('wereda_id', '=', wereda_id), ('is_leader', '=', False), ('member_cells', '=', False), ('is_league', '=', False)]")
    date_of_meeting = fields.Date()
#    date_of_meeting_ethiopian = fields.Date(store=True)
    place_of_meeting = fields.Char(translate=True)
    time_of_meeting = fields.Float()
    total = fields.Integer(store=True)
    leaders_ids = fields.Many2many('res.partner', 'leader_cell_rel', domain="['&', '&', ('is_leader', '=', True), ('wereda_id', '=', wereda_id), ('member_cells', '=', False), ('is_league', '=', False)]", string="Leaders")
    all_partners = fields.Many2many('res.partner', 'all_partner_rel', store=True)
    total_members = fields.Integer(compute="_calculate_total_members", store=True)
    total_leaders = fields.Integer(compute="_assign_leaders_cells", store=True)
    total_leader_fee = fields.Float(compute="_calculate_leader_fee", store=True)
    total_member_fee = fields.Float(compute="_calculate_member_fee", store=True)
    total_membership_fee = fields.Float(compute="_compute_totals", store=True)
    total = fields.Integer(compute="_all_members", store=True)

    # def write(self, vals):
    #     """This function will compute the dates"""
    #     try:
    #         if vals['date_of_meeting'] is not None:
    #             date_str = str(vals['date_of_meeting']).split(' ')[0]
    #             date_time_obj = date_str.split('-')
    #             Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
    #             vals['date_of_meeting_ethiopian'] = Edate
    #     except:
    #         pass
    #     return super(Cells, self).write(vals) 


    @api.depends('leaders_ids')
    def _assign_leaders_cells(self):
        """This function will assign leaders their respective main office and cells"""
        for record in self:
            total = 0.00
            record.total_leaders = len(record.leaders_ids.ids)
            if record.leaders_ids:
                for leader in record.leaders_ids:
                    leader.write({
                        'main_office': record.main_office.id,
                        'member_cells': record.id
                    })
                    total += (leader.membership_monthly_fee_cash + leader.membership_monthly_fee_cash_from_percent)
            record.total_leader_fee = total

    @api.depends('members_ids')
    def _calculate_total_members(self):
        """This function will calculate the total members"""
        for record in self:
            total = 0.00
            record.total_members = len(record.members_ids.ids)
            if record.members_ids:
                for memb in record.members_ids:
                    memb.write({
                        'main_office': record.main_office.id,
                        'member_cells': record.id
                    })
                    total += (memb.membership_monthly_fee_cash + memb.membership_monthly_fee_cash_from_percent)
            record.total_member_fee = total

    @api.depends('total_members', 'total_leaders')
    def _all_members(self):
        """Collect all in one"""
        for record in self:
            if record.total_members or record.total_leaders:
                record.total = record.total_members + record.total_leaders

    # @api.onchange('leaders_ids')
    # def _count_leaders(self):
    #     """This function will count the total leaders"""
    #     for record in self:
    #         if record.leaders_ids:
    #             total = len(record.leaders_ids.ids)
    #             if total > 3:
    #                 raise UserError(_("A Cell Shouldn't Have More Than 3 Leaders"))

    # @api.onchange('members_ids')
    # def _check_total_members(self):
    #     """This function will check if they have the right number of members"""
    #     for record in self:
    #         if record.members_ids:
    #             total = len(record.members_ids.ids)
    #             if total > 35:
    #                 raise UserError(_("A Cell Shouldn't Have More Than 35 Members"))


    @api.depends('total_leader_fee', 'total_member_fee')
    def _compute_totals(self):
        """This function will compute the total fee and total members"""
        for record in self:
            if record.total_member_fee or record.total_leader_fee:
                record.total_membership_fee = record.total_leader_fee + record.total_member_fee