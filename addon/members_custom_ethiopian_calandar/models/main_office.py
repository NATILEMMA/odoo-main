
import random
import string
import werkzeug.urls

from collections import defaultdict
from datetime import datetime, date 
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
import logging
_logger = logging.getLogger(__name__)
pick1 = []
pick2 = []
pick3 = []
pick4 = []




class MainOffice(models.Model):
    _inherit="main.office"


    ethiopian_date_of_meeting_cells = fields.Date(string="In Ethiopian date of meeting cells")
    ethiopian_date_of_meeting_eachother = fields.Date(string="In Ethiopian date of meeting eachother")
  

    @api.model
    def create(self, vals):
        for i in range(0, len(pick1)):
  
            if i == (len(pick1)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick1[i]['year'],pick1[i]['month'],pick1[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick1[i]['pick'] == 1:
                    vals['date_of_meeting_eachother'] = date1
                    vals['ethiopian_date_of_meeting_eachother'] = Edate1
                    pick1.clear()
                
        for i in range(0, len(pick2)):
        
            if i == (len(pick2)-1):
                date1 = EthiopianDateConverter.to_gregorian(pick2[i]['year'],pick2[i]['month'],pick2[i]['day'])
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                if pick2[i]['pick'] == 2: 
                    vals['date_of_meeting_cells'] = date1
                    vals['ethiopian_date_of_meeting_cells'] = Edate1
                    pick2.clear()
        try:
            if vals['date_of_meeting_eachother'] and vals['date_of_meeting_cells'] is not None:
                date1 = vals['date_of_meeting_eachother']
                date2 = vals['date_of_meeting_cells']
                Edate1 = EthiopianDateConverter.to_ethiopian(date1.year,date1.month,date1.day)
                Edate2 = EthiopianDateConverter.to_ethiopian(date2.year,date2.month,date2.day)
                vals['ethiopian_date_of_meeting_eachother'] = Edate2
                vals['ethiopian_date_of_meeting_cells'] = Edate1
        except:
            pass
       
        return super(MainOffice, self).create(vals)



    def write(self, vals):
        _logger.info("############# Write:%s",vals)
        try:
            if vals['date_of_meeting_eachother'] is not None:
                date_str = vals['date_of_meeting_eachother']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                vals['ethiopian_date_of_meeting_eachother'] = Edate
        except:
            pass
        try:
            if vals['date_of_meeting_cells'] is not None:
                
                date_str = vals['date_of_meeting_cells']
                date_time_obj = date_str.split('-')
                Edate = EthiopianDateConverter.to_ethiopian(int(date_time_obj[0]),int(date_time_obj[1]),int(date_time_obj[2]))
                vals['ethiopian_date_of_meeting_cells'] = Edate
        except:
            pass
       
        # self.action_reload_page()
        return super(MainOffice, self).write(vals)


    @api.model
    def date_convert_and_set(self,picked_date):
        try:
            dd = picked_date['url'].split('id=')
            id = str(dd[1]).split('&')
            m = picked_date['url'].split('model=')
            mm = m[1].split('&')
            if len(id[0]) <= 0:
                _logger.info("################# not fund")

            else:
                    models = mm[0]
                    search = self.env[models].search([('id','=',id[0])])
                    date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
                    date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
                    if models == "main.office":
                        if picked_date['pick'] == 1:
                            search.update({
                                'date_of_meeting_eachother': date_gr,
                                'ethiopian_date_of_meeting_eachother': date
                                })
                            # return {
                            #         'type': 'ir.actions.client',
                            #         'tag': 'reload',
                            #     }
                            # self.env.cr.commit()
                            # return search
                            search.action_reload_page()
                             

                        if picked_date['pick'] == 2:
                            search.update({
                                'date_of_meeting_cells': date_gr,
                                'ethiopian_date_of_meeting_cells':date
                                })
                            # return {
                            #         'type': 'ir.actions.client',
                            #         'tag': 'reload',
                            #     }
                            # self.env.cr.commit()
                            # return search 
                            search.action_reload_page()
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
        except:
            pass
        date_gr = EthiopianDateConverter.to_gregorian(picked_date['year'], picked_date['month'], picked_date['day'])
        date,time = str(datetime.now()).split(" ")
        _logger.info(str(date_gr) + " " + str(f"{time}"))
        dd,mm,yy= picked_date['day'],picked_date['month'],picked_date['year']
        # date = str(date_et) + " " + str(f"{time}")
        date = EthiopianDateConverter.to_ethiopian(date_gr.year,date_gr.month,date_gr.day)
        date = {"data":f"d={picked_date['day']},m={picked_date['month']},y={picked_date['year']}","date":date}
        data = {
            'day':   picked_date['day'],
            'month': picked_date['month'],
            'year': picked_date['year'],
            'pick': picked_date['pick']
        }
        if picked_date['pick'] == 1:
            pick1.append(data)
        if picked_date['pick'] == 2:
            pick2.append(data)
        if picked_date['pick'] == 3:
            pick3.append(data)
        if picked_date['pick'] == 4:
            pick3.append(data)

