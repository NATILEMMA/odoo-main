# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ctypes import sizeof
from http import client
import base64
import babel.messages.pofile
import base64
import copy
import datetime
import functools
import glob
import hashlib
import io
import itertools
import jinja2
import json
import logging
import pprint
import operator
import os
import re
import sys
import tempfile
# from numpy import True_

import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from collections import OrderedDict, defaultdict, Counter
from werkzeug.urls import url_encode, url_decode, iri_to_uri
from lxml import etree
import unicodedata
from datetime import timedelta,datetime

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR
from odoo import fields, http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.event.controllers.main import EventController
from odoo.http import request
from odoo.osv import expression
from odoo.tools.misc import get_lang, format_date



import werkzeug
from werkzeug.datastructures import OrderedMultiDict
from werkzeug.exceptions import NotFound

from ast import literal_eval
from collections import defaultdict
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import odoo
from odoo.addons.base.models.res_partner import Partner
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_module_path, get_resource_path
from odoo.tools import image_process, topological_sort, html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property, float_repr
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open
from odoo import http, tools
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception, Response
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security
from odoo.addons.auth_signup.models.res_users import SignupError

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.osv.expression import OR
from odoo import fields, http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request
from odoo.tools.misc import get_lang
from odoo.addons.portal.controllers.portal import CustomerPortal




_logger = logging.getLogger(__name__)
import string
import base64
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging

_logger = logging.getLogger(__name__)

# class PortalAccountDetail(CustomerPortal):

#     CustomerPortal.MANDATORY_BILLING_FIELDS.remove("street")
#     CustomerPortal.MANDATORY_BILLING_FIELDS.remove("email")
#     CustomerPortal.MANDATORY_BILLING_FIELDS.remove("country_id")
#     CustomerPortal.OPTIONAL_BILLING_FIELDS.extend(["title",
#                                                    "is_company",
#                                                    "gender",
#                                                    "date",
#                                                    "employment_status",
#                                                    "ethnicity",
#                                                    "subcity_id",
#                                                    "wereda_id",
#                                                    "country_id",
#                                                    "street",
#                                                    "email"])

#     @http.route(['/my/account'], type='http', auth='user', website=True)
#     def account(self, redirect=None, **post):
#         if post and request.httprequest.method == 'POST':
#             for field in set(['subcity_id', 'title', 'wereda_id']) & set(post.keys()):
#                 try:
#                     post[field] = int(post[field])
#                 except:
#                     post[field] = False
#             image_1920 = post.get('image_1920')
#             date = post.get('date')
#             gender = post.get('gender')
#             ethnicity = post.get('ethnicity')
#             employment_status = post.get('employment_status')
#             title = post.get('title')
#             subcity_id = post.get('subcity_id')
#             wereda_id = post.get('wereda_id')
#             if image_1920:
#                 image_1920 = image_1920.read()
#                 image_1920 = base64.b64encode(image_1920)
#                 request.env.user.partner_id.sudo().write({
#                     'image_1920': image_1920,
#                     'date': date,
#                     'gender': gender,
#                     'ethnicity': ethnicity,
#                     'employment_status': employment_status,
#                     'title': title,
#                     'subcity_id': subcity_id,
#                     'wereda_id': wereda_id
#                 })
#             post.pop('image_1920')
#         titles = request.env['res.partner.title'].sudo().search([])
#         subcities = request.env['membership.handlers.parent'].sudo().search([])
#         weredas = request.env['membership.handlers.branch'].sudo().search([])
#         req = super().account(redirect=redirect, **post)
#         # The qcontext will hold contexts to be added to the template.
#         # It can be edited from a Response instance(object)
#         req.qcontext.update({'titles': titles,
#                              'subcities': subcities,
#                              'weredas': weredas})
#         return req


# class PortalAccountDetail(CustomerPortal):

#     CustomerPortal.OPTIONAL_BILLING_FIELDS.extend(["product_id", "title", "is_company", "gender", "date", "employment_status", "ethnicity", "department_id"])
#     @http.route(['/my/profile'], type='http', auth='user', website=True) 
#     def account(self, redirect=None, **post):
#         if post and request.httprequest.method == 'POST':
#             free_member = False
#             for field in set(['department_id', 'title', 'product_id']) & set(post.keys()):
#                 try:
#                     post[field] = int(post[field])
#                 except:
#                     post[field] = False
#             image_1920 = post.get('image_1920')
#             date = post.get('date')
#             gender = post.get('gender')
#             ethnicity = post.get('ethnicity')
#             employment_status = post.get('employment_status')
#             title = post.get('title')
#             department_id = post.get('department_id')
#             product_id = post.get('product_id')
#             if product_id == False:
#               free_member = True
#             print(product_id)
#             print(free_member)
#             if image_1920:
#                 image_1920 = image_1920.read()
#                 image_1920 = base64.b64encode(image_1920)
#                 request.env.user.partner_id.sudo().write({
#                     'image_1920': image_1920,
#                     'date': date,
#                     'gender': gender,
#                     'ethnicity': ethnicity,
#                     'employment_status': employment_status,
#                     'title': title,
#                     'department_id': department_id,
#                     'product_id': product_id,
#                     'free_member': free_member
#                 })
#             post.pop('image_1920')
#         membership_product = request.env['product.template'].sudo().search([('membership', '=', True)])
#         departments = request.env['hr.department'].sudo().search([])
#         titles = request.env['res.partner.title'].sudo().search([])
#         req = super().account(redirect=redirect, **post)
#         # The qcontext will hold contexts to be added to the template.
#         # It can be edited from a Response instance(object)
        
#         return http.request.render('member_dashboard.portal_my_details', {'departments': departments,
#                              'titles': titles,
#                              'membership_product': membership_product})




class WebRegisteration(AuthSignupHome):
    
    
    @http.route('/success', type='http',  auth='public', website=True)
    def reset_password(self,  **kw):
        return http.request.redirect('/shop')
  

    @http.route('/my/dashboard', type='http',  auth='public', website=True)
    def mydashboard(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, search=None, search_in='content', groupby=None,   **kw):
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id

        return http.request.render('member_dashboard.my_dashboard',{
            # "projects":project,"total_sales":total_sales,"total_vistor":total_vistor,
            "users":users,})

    @http.route('/complaint/<int:id>/edit', type='http', auth='user', website='True')
    def edit_customize(self, id, **kwargs):
        """This function will edit the complaint on the form"""
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        request.redirect('/my/create_complaint')
        complaint = request.env['member.complaint'].sudo().search([('id', '=', id)])
        perpertrators = request.env['res.partner'].sudo().search(['|', ('is_member', '=', True), ('is_leader', '=', True)])
        return request.render("member_dashboard.complaint_form",
        {
            'complaint': complaint,
            'perpertrators': perpertrators,
            "users":users
        })

    @http.route('/complaint/<int:id>/delete', type='http', auth='user', website='True')
    def delete_complaint(self, id, **kwargs):
        """This function will delete the complaint on the from database"""
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        complaint = request.env['member.complaint'].sudo().search([('id', '=', id)])
        complaint.unlink()
        return request.redirect('/my/complaint',{"users":users})
    

   

    @http.route('/add_complaint', type='http', auth='user', website='True')
    def complaint_entry(self, **kwargs):
        """This function will handle the entry and editing of a new complaint"""
        # The following statement will get a list of ids from the selected values in form
        # [(6, 0, ids)] also means create a record for  many2many and one2many
        _logger.info("################")
        _logger.info(kwargs)
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id
        complaint = request.env['member.complaint'].sudo().search([('victim_id', '=', user.id)])
        perps = request.httprequest.form.getlist('perpertrators')
        if kwargs.get('complaint'):
          complaint = request.env['member.complaint'].sudo().search([('id', '=', kwargs.get('complaint'))])

          # This allows for temporary deletion of records in the relation table for perpetrators
          # Before it can be cleaned and new records can be added
          for id in perps:
            complaint.sudo().write({
              'perpertrators': [(3, int(id))]
            })
          complaint.sudo().write({
            'subject': kwargs.get('subject'),
            'circumstances': kwargs.get('circumstances'),
            'state': 'updated',
            'victim_id': user.id,
            'perpertrators': [
              (
                6,
                0,
                perps
              )
            ]
            
           })
          return request.redirect('/my/complaint')
        else:
            cat = kwargs.get('complaint_category')
            request.env['member.complaint'].sudo().create({
            'subject': kwargs.get('subject'),
            'circumstances': kwargs.get('circumstances'),
            'victim_id': user.id,
            'perpertrators': [
              (
                6,
                0,
                perps
              )
            ]
            })
            return request.render("member_dashboard.complaint_end", {})


    @http.route('/my/complaint', type='http', auth='user', website='True', methods=['GET'])
    def complaint_data(self, **kwargs):
        """This function will handle the displaying for complaints"""
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id
        complaint = request.env['member.complaint'].sudo().search([('victim_id', '=', user.id)])
        return request.render("member_dashboard.complaint_list", {'record': complaint,"users":users})


    @http.route('/my/create_complaint', type='http', auth='user', website='True')
    def complaint_saving(self, **kwargs):
        """This function will access and populate a new form for complaint"""
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id
        perpertrators = request.env['res.partner'].sudo().search(['|', ('is_member', '=', True), ('is_leader', '=', True)])
        return request.render("member_dashboard.complaint_form_add",
        {
            'complaint': {'id': None, 'subject': None, 'circumstances': None, 'perpertrators': None},
            'perpertrators': perpertrators,
            'users': users
        })


    @http.route('/my/add_attachments', type='http', auth='user', website='True')
    def add_attachments(self, **kwargs):
       """This function will attach files with member"""
       partner = request.env.user.partner_id
       users = request.env['res.partner'].search([('id','=',partner.id)])
       if kwargs.get('attach_id'):
         description = kwargs.get('description')
         attached_files = request.httprequest.files.getlist('attachment_ids')
         type = kwargs.get('attachment_type')
         rec = request.env['ir.attachment'].sudo().search([('id', '=', kwargs.get('attach_id'))])
         data_obj = {
            'res_model': 'res.partner',
            'res_id': partner.id,
            'attachment_type': type,
            'description': description
         }
         for attach in attached_files:
            if bool(attach.filename):
                attached_file = attach.read()
                data_obj['name'] = attach.filename
                data_obj['type'] = 'binary'
                data_obj['datas'] = base64.b64encode(attached_file)
         rec.update(data_obj)
         return request.redirect('/my/add_attachments')

       if 'attachment_ids' in request.params and kwargs and request.httprequest.method == 'POST':
         type = kwargs.get('attachment_type')
         description = kwargs.get('description')
         attached_files = request.httprequest.files.getlist('attachment_ids')
         for attach in attached_files:
             attached_file = attach.read()
             request.env['ir.attachment'].sudo().create({
                 'name': attach.filename,
                 'res_model': 'res.partner',
                 'res_id': partner.id,
                 'attachment_type': type,
                 'description': description,
                 'type': 'binary',
                 'datas': base64.b64encode(attached_file)
             })
         return request.redirect('/my/add_attachments')
       attachment_type = request.env['attachment.type'].sudo().search([])
       attachment = request.env['ir.attachment'].sudo().search([('res_id', '=', partner.id)])
       return request.render("member_dashboard.attachment_form",
        {
            'object': {'id': None, 'description': None, 'attachment_type': {'id': None, 'name': None}},
            'attachment_type': attachment_type,
            'attachment': attachment,
            'root': '/my/add_attachments',
            'users': users
        })

    @http.route('/my/add_attachments/<int:id>/<string:action>', auth='public', website=True)
    def attachment_action(self, id, action, **kw):
        partner = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner.id)])
        rec = request.env['ir.attachment'].sudo().search([('id', '=', id)])
        if action == 'edit':
            partner = request.env.user.partner_id
            attachment_type = request.env['attachment.type'].sudo().search([])
            attachment = request.env['ir.attachment'].sudo().search([('res_id', '=', partner.id)])
            return http.request.render('member_dashboard.attachment_form', {
                 'object': rec,
                 'root': '/my/add_attachments',
                 'attachment_type': attachment_type,
                 'attachment': attachment,
                 'users': users
            })
        if action == 'delete':
            rec.unlink()
            return request.redirect('/my/add_attachments')

    @http.route(['/my/profileacc'], type='http', auth='user', website=True)
    def profile(self, redirect=None, **post):
        if post and request.httprequest.method == 'POST':
            values = {}
            values.update(post)
            for field in set(['subcity_id', 'region', 'wereda_id', 'ed_level']) & set(values.keys()):
                try:
                    values[field] = int(values[field])
                except:
                    values[field] = False
            if values['income']:
                values['income'] = float(values['income'])
            else:
                values['income'] = 0.00
            if values['image_1920']:
                values['image_1920'] = values['image_1920'].read()
                values['image_1920'] = base64.b64encode(values['image_1920'])
                if values['income'] == 0.00:
                    request.env.user.partner_id.sudo().write({
                        'payment_method': 'cash',
                        'membership_monthly_fee_percent': 0.00,
                        'membership_monthly_fee_cash': 0.00
                    })
                else:
                    all_fee = request.env['payment.fee.configuration'].search([])
                    for fee in all_fee:
                        if fee.minimum_wage <= values['income'] <= fee.maximum_wage:
                            request.env.user.partner_id.sudo().write({
                                'payment_method': 'percentage',
                                'membership_monthly_fee_percent': fee.fee_in_percent,
                                'membership_monthly_fee_cash_from_percent': (fee.fee_in_percent / 100) * values['income'],
                            })
                            break
                        else:
                            request.env.user.partner_id.sudo().write({
                                'payment_method': 'percentage',
                                'membership_monthly_fee_percent': fee.fee_in_percent,
                                'membership_monthly_fee_cash_from_percent': (fee.fee_in_percent / 100) * values['income'],
                            })
                            continue
                current = request.env.user.partner_id.work_experience_ids.filtered(lambda rec: rec.current_job == True)
                if current.name == values['function'] and current.place_of_work == values['company_name'] and current.years_of_service == values['years_of_service']:
                    current.write({
                        'current_job': True
                    })                    
                if current.name == values['function'] and current.place_of_work == values['company_name'] and current.years_of_service != values['years_of_service']:
                    current.write({
                        'years_of_service': values['years_of_service']
                    })
                if current.name != values['function']:                      
                    current.write({
                        'current_job': False
                    })                    
                    request.env.user.partner_id.sudo().write({
                        'work_experience_ids': [(0, 0, {
                            'name': values['function'],
                            'place_of_work': values['company_name'],
                            'years_of_service': values['years_of_service'],
                            'current_job': True
                        })],
                    })
                if (not current) and (values['function'] and values['company_name'] and values['years_of_service']):
                    request.env.user.partner_id.sudo().write({
                        'work_experience_ids': [(0, 0, {
                            'name': values['function'],
                            'place_of_work': values['company_name'],
                            'years_of_service': values['years_of_service'],
                            'current_job': True
                        })]
                    })                
                if not values['function'] and not values['company_name'] and not values['years_of_service']:
                    current = request.env.user.partner_id.work_experience_ids.filtered(lambda rec: rec.current_job == True)
                    if current:
                        current.write({
                            'current_job': False
                        })
                values.pop('company_name')
                values.pop('function')
                values.pop('years_of_service')
                request.env.user.partner_id.sudo().write(values)
                return request.redirect('/my/profileacc')
            else:
                if values['income'] == 0.00:
                    request.env.user.partner_id.sudo().write({
                        'payment_method': 'cash',
                        'membership_monthly_fee_percent': 0.00,
                        'membership_monthly_fee_cash': 0.00,
                        'income': values['income']
                    })
                else:
                    all_fee = request.env['payment.fee.configuration'].search([])
                    for fee in all_fee:
                        if fee.minimum_wage <= values['income'] <= fee.maximum_wage:
                            request.env.user.partner_id.sudo().write({
                                'payment_method': 'percentage',
                                'membership_monthly_fee_percent': fee.fee_in_percent,
                                'membership_monthly_fee_cash_from_percent': (fee.fee_in_percent / 100) * values['income'],
                                'income': values['income']
                            })
                            break
                        else:
                            request.env.user.partner_id.sudo().write({
                                'payment_method': 'percentage',
                                'membership_monthly_fee_percent': fee.fee_in_percent,
                                'membership_monthly_fee_cash_from_percent': (fee.fee_in_percent / 100) * values['income'],
                                'income': values['income']
                            })
                            continue 
                current = request.env.user.partner_id.work_experience_ids.filtered(lambda rec: rec.current_job == True)
                if current.name == values['function'] and current.place_of_work == values['company_name'] and current.years_of_service == values['years_of_service']:
                    current.write({
                        'current_job': True
                    })                    
                if current.name == values['function'] and current.place_of_work == values['company_name'] and current.years_of_service != values['years_of_service']:
                    current.write({
                        'years_of_service': values['years_of_service']
                    })
                if current.name != values['function']:                      
                    current.write({
                        'current_job': False
                    })                    
                    request.env.user.partner_id.sudo().write({
                        'work_experience_ids': [(0, 0, {
                            'name': values['function'],
                            'place_of_work': values['company_name'],
                            'years_of_service': values['years_of_service'],
                            'current_job': True
                        })],
                    })
                if (not current) and (values['function'] and values['company_name'] and values['years_of_service']):
                    request.env.user.partner_id.sudo().write({
                        'work_experience_ids': [(0, 0, {
                            'name': values['function'],
                            'place_of_work': values['company_name'],
                            'years_of_service': values['years_of_service'],
                            'current_job': True
                        })]
                    })                
                if not values['function'] and not values['company_name'] and not values['years_of_service']:
                    current = request.env.user.partner_id.work_experience_ids.filtered(lambda rec: rec.current_job == True)
                    if current:
                        current.write({
                            'current_job': False
                        })
                values.pop('company_name')
                values.pop('function')
                values.pop('years_of_service')
                request.env.user.partner_id.sudo().write(values)
                return request.redirect('/my/profileacc')
        partner = request.env.user.partner_id
        place = ''
        job = ''
        year = ''
        if len(partner.work_experience_ids) > 0:
            current = partner.work_experience_ids.filtered(lambda rec: rec.current_job == True)
            place = current.place_of_work
            job = current.name
            year = current.years_of_service
        users = request.env['res.partner'].search([('id','=',partner.id)])
        subcities = request.env['membership.handlers.parent'].sudo().search([])
        weredas = request.env['membership.handlers.branch'].sudo().search([])
        ed_levels = request.env['res.edlevel'].sudo().search([])
        regions = request.env['res.country.state'].sudo().search([('country_id', '=', 69)])
        return request.render("member_dashboard.new_portal_my_details", { 'partner': partner,
                                                                          'users': users,
                                                                          'subcities': subcities,
                                                                          'weredas': weredas,
                                                                          'ed_levels': ed_levels,
                                                                          'regions': regions,
                                                                          'place': place,
                                                                          'job': job,
                                                                          'year': year
                                                                        })
   
 
    @http.route('/contact-us', type='http',  auth='public', website=True)
    def contactus(self,  **kw):
        company = request.env['res.company'].sudo().search([])

        
        return http.request.render('member_dashboard.contact_us',{"company":company})

    @http.route('/my/chart', type='http',  auth='public', website=True)
    def mychart(self,  **kw):
        return http.request.render('member_dashboard.my_chart')



    @http.route('/report/feedback', type='http',  auth='public', website=True)
    def myreports(self,  **kw):
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id
        return http.request.render('member_dashboard.my_report', {"users":users, })

    
    def sitemap_event(env, rule, qs):
        if not qs or qs.lower() in '/events':
            yield {'loc': '/events'}

    @http.route(['/my/event', '/event/page/<int:page>', '/events', '/events/page/<int:page>'], type='http', auth="public", website=True, sitemap=sitemap_event)
    def events(self, page=1, **searches):
        Event = request.env['event.event']
        EventType = request.env['event.type']
        partner_id = request.env.user.partner_id
        _logger.info(partner_id)
        mentee_id =  request.session.uid
        search_from_res_users = request.env['res.users'].search([('id','=', mentee_id)])
        _logger.info(search_from_res_users)
        search_from_res_partner = request.env['res.partner'].search([('id','=',partner_id.id)])
        _logger.info(search_from_res_partner)
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])

        searches.setdefault('search', '')
        searches.setdefault('date', 'all')
        searches.setdefault('type', 'all')
        searches.setdefault('country', 'all')

        website = request.website

        def sdn(date):
            return fields.Datetime.to_string(date.replace(hour=23, minute=59, second=59))

        def sd(date):
            return fields.Datetime.to_string(date)
        today = datetime.today()
        dates = [
            ['all', _('Next Events'), [("date_end", ">", sd(today))], 0],
            ['today', _('Today'), [
                ("date_end", ">", sd(today)),
                ("date_begin", "<", sdn(today))],
                0],
            ['week', _('This Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=-today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=6-today.weekday())))],
                0],
            ['nextweek', _('Next Week'), [
                ("date_end", ">=", sd(today + relativedelta(days=7-today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=13-today.weekday())))],
                0],
            ['month', _('This month'), [
                ("date_end", ">=", sd(today.replace(day=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['nextmonth', _('Next month'), [
                ("date_end", ">=", sd(today.replace(day=1) + relativedelta(months=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=2)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['old', _('Past Events'), [
                ("date_end", "<", today.strftime('%Y-%m-%d 00:00:00'))],
                0],
        ]

        # search domains
        domain_search = {'website_specific': website.website_domain()}

        if searches['search']:
            domain_search['search'] = [('name', 'ilike', searches['search'])]

        current_date = None
        current_type = None
        current_country = None
        for date in dates:
            if searches["date"] == date[0]:
                domain_search["date"] = date[2]
                if date[0] != 'all':
                    current_date = date[1]

        if searches["type"] != 'all':
            current_type = EventType.browse(int(searches['type']))
            domain_search["type"] = [("event_type_id", "=", int(searches["type"]))]

        if searches["country"] != 'all' and searches["country"] != 'online':
            current_country = request.env['res.country'].browse(int(searches['country']))
            domain_search["country"] = ['|', ("country_id", "=", int(searches["country"])), ("country_id", "=", False)]
        elif searches["country"] == 'online':
            domain_search["country"] = [("country_id", "=", False)]

        def dom_without(without):
            domain = [('state', "in", ['draft', 'confirm', 'done'])]
            for key, search in domain_search.items():
                if key != without:
                    domain += search
            return domain

        # count by domains without self search
        for date in dates:
            if date[0] != 'old':
                date[3] = Event.search_count(dom_without('date') + date[2])

        domain = dom_without('type')
        types = Event.read_group(domain, ["id", "event_type_id"], groupby=["event_type_id"], orderby="event_type_id")
        types.insert(0, {
            'event_type_id_count': sum([int(type['event_type_id_count']) for type in types]),
            'event_type_id': ("all", _("All Categories"))
        })

        domain = dom_without('country')
        countries = Event.read_group(domain, ["id", "country_id"], groupby="country_id", orderby="country_id")
        countries.insert(0, {
            'country_id_count': sum([int(country['country_id_count']) for country in countries]),
            'country_id': ("all", _("All Countries"))
        })

        step = 12  # Number of events per page
        event_count = Event.search_count(dom_without("none"))
        pager = website.pager(
            url="/event",
            url_args=searches,
            total=event_count,
            page=page,
            step=step,
            scope=5)

        order = 'date_begin'
        if searches.get('date', 'all') == 'old':
            order = 'date_begin desc'
        if searches["country"] != 'all':   # if we are looking for a specific country
            order = 'is_online, ' + order  # show physical events first
        order = 'is_published desc, ' + order
        events = Event.search(dom_without("none"), limit=step, offset=pager['offset'], order=order)

        keep = QueryURL('/event', **{key: value for key, value in searches.items() if (key == 'search' or value != 'all')})

        values = {
            'current_date': current_date,
            'current_country': current_country,
            'current_type': current_type,
            'event_ids': events,  # event_ids used in website_event_track so we keep name as it is
            'dates': dates,
            'types': types,
            'countries': countries,
            'pager': pager,
            'searches': searches,
            "users":users, "search_from_res_users":search_from_res_users,
            'keep': keep,
        }

        if searches['date'] == 'old':
            # the only way to display this content is to set date=old so it must be canonical
            values['canonical_params'] = OrderedMultiDict([('date', 'old')])

        return request.render("member_dashboard.index", values)




    @http.route('/register/reset_password', type='http',  auth='public', website=True)
    def reset_password(self,  **kw):
        return http.request.render('custom_web.reset_password')
    
        
    @http.route('/my/profile', type='http',  auth='public', website=True)
    def my_profile(self,  **kw):
        
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id
        return http.request.render('member_dashboard.my_profile',{"users":users})
          
        
    @http.route('/api/fileupload', type='json', auth='public', website=True, csrf=False, method=['GET'])
    def upload_image(self, **kw):
        _logger.info("##############IN UPLOAD ##############")
        _logger.info(request.httprequest.files.getlist('image'))
        _logger.info(request.httprequest.files.getlist('file'))
        _logger.info(kw)
        
        files = request.httprequest.files.getlist('file')
        _logger.log("########### files:%s",files)

   
    #membership feedback 
    @http.route('/feedback_submit',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def membership_feedback(self, *args, **kw):
        _logger.info(kw)
        if kw and request.httprequest.method == 'POST':
            _logger.info("__________________________")
            partner_id = request.env.user.partner_id
            today = datetime.today()
            feedback = request.env['report.report'].sudo().create({
                "user_id": kw.get('user_id'),
                # "date": today,
                "how_did_you_find": kw.get('how_did_you_find'),
                "how_often_do_you": kw.get('how_often_do_you'),
                "your_participation": kw.get('your_participation'),
                "rate_your_level": kw.get('rate_your_level'),
                "how_do_you_evaluate": kw.get('how_often_do_you'),
                "suggestions": kw.get('suggestions') 
                })

            _logger.info(feedback)
            # return werkzeug.utils.redirect('/my/dashboard')
            return request.render('member_dashboard.feedback_submitted')


    #Shear Ideas 
    @http.route('/api/shear/ideas',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def shearIdeas(self, *args, **kw):
        _logger.info(kw)
        if kw and request.httprequest.method == 'POST':
            _logger.info("__________________________")
            partner_id = request.env.user.partner_id
            today = datetime.today()
            country = request.env['res.country'].sudo().search([('id','=',kw.get("country_id"))])

            shearIdea = request.env['crm.lead'].sudo().create({
                "comment_type": "Ideas Sheared",
                "name": "Ideas Sheared by  " + kw.get('name'),
                "volunteer_name": kw.get('your_participation'),
                "volunteer_email": kw.get('email'),
                "email_from": kw.get('email'),
                "volunteer_address": kw.get('address'),
                "volunteer_country": country.id,
                "what_do_you_want": kw.get('what_do_you_want') ,
                "never_again": kw.get('never_again') 

                })

           
            return werkzeug.utils.redirect('/contactus-thank-you')
            # return request.render('member_dashboard.feedback_submitted')


    #Contact Us
    @http.route('/api/contact_us',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def contact_Us(self, *args, **kw):
        _logger.info(kw)
        if kw and request.httprequest.method == 'POST':
            _logger.info("__________________________")
            partner_id = request.env.user.partner_id
            today = datetime.today()
            country = request.env['res.country'].sudo().search([('id','=',kw.get("country_id"))])

            shearIdea = request.env['crm.lead'].sudo().create({
                "comment_type": "Comment",
                "name": "Commented by  " + kw.get('name'),
                "email_from": kw.get('email'),
                "phone": kw.get('phone'),
                "description":  kw.get('subject')+"\n\n"+ kw.get('message'),
               

                })

           
            return werkzeug.utils.redirect('/contactus-thank-you')
            # return request.render('member_dashboard.feedback_submitted')


    
   
    #membership compliant 
    @http.route('/complian_submit',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def membership_complaint(self, *args, **kw):
        _logger.info(kw)
        if kw and request.httprequest.method == 'POST':
            _logger.info("__________________________")
            partner_id = request.env.user.partner_id
            complaint = request.env['member.complaint'].sudo().create({
                "user_id": kw.get('user_id'),
                "victim_id": kw.get('victim_id'),
                "subject": kw.get('subject'),
                "complaint_category": kw.get('complaint_id'),
                "circumstances": kw.get('message') 
                })

            _logger.info(complaint) 
            return request.render('member_dashboard.complaint_submitted')

            # return request.render('member_dashboard.my_dashboard')

    
    #Thanks popup
    @http.route('/complian/submit', type='http', auth='public', website=True, sitemap=False)
    def complian(self, *args, **kw):
        _logger.info(kw)

        partner_id = request.env.user.partner_id
        _logger.info(partner_id)
        mentee_id =  request.session.uid
        search_from_res_users = request.env['res.users'].search([('id','=', mentee_id)])
        _logger.info(search_from_res_users)
        search_from_res_partner = request.env['res.partner'].search([('id','=',partner_id.id)])
        _logger.info(search_from_res_partner)
        users = request.env['mentor.mapping'].sudo().search([('mentee_id','=',partner_id.id)])
        users_mentor = request.env['mentor.mapping'].sudo().search([('mentor_id','=',search_from_res_partner.id)])
        _logger.info(users)
        _logger.info(users_mentor)
        partner_id = request.env.user.partner_id
        partner_id = request.env.user.partner_id
        users = request.env['res.partner'].search([('id','=',partner_id.id)])
       
        return request.render('member_dashboard.complaint_submitted',{"partner_id":partner_id,"users":users, })
                

   
      
    #Mentroship Registration api

    @http.route('/membership_signup',methods=['POST'], type='http', auth='public', website=True, sitemap=False)
    def membership_signup(self, *args, **kw):
        _logger.info(kw)
        qcontext = self.get_auth_signup_qcontext()
        print(kw)
        _logger.info("qcontext: %s",qcontext)
        
        # FileStorage = kw.get('image_1920')
        # FileData = FileStorage.read()
        # file_base64 = base64.encodestring(FileData)


        # name = kw.get('image_1920').filename
        # file = kw.get('image_1920')

        # profile = {
        #     'image_1920_1920':base64.b64encode(file.read()),

        # }

        # files = request.httprequest.files.getlist('image_1920')
        # attachment = files.read()
        # 'image_1920_1920': base64.encodestring(attachment)
        # post['image_1920'].read().encode('base64')}

        projects = request.httprequest.form.getlist('projects[]')
        mentees = request.httprequest.form.getlist('mentees[]')
        
        try:
            self.do_signup(qcontext)
            # Send an account creation confirmation email
            if qcontext.get('token'):
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
            _logger.info("________________________ Writing custom feilds_____________________________")
            partner_id = request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1)
            res_user_id = request.env['res.users'].sudo().search([('login','=', kw.get('login'))], limit=1)
            mentee_id = request.env['res.partner'].sudo().search([('id','=', mentees)], limit=1)
            mentor_id = request.env['res.partner'].sudo().search([('name','=', kw.get('name')),('email','=',kw.get('login'))], limit=1)
            # request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1).write({"free_member": "1",   
            #         "image_1920":file_base64})
            # _logger.info(projects)
            vals = []
            pro = {}
            for project in projects:
                
                product_id = request.env['project.project'].sudo().search([('id','=', project)], limit=1)
                _logger.info(product_id)
                pro['project_contribute'] = product_id
                
                vals.append(pro)
            _logger.info(vals)
            country = request.env['res.country'].sudo().search([('id','=',kw.get("country_id"))])
            country_state = request.env['res.country.state'].sudo().search([('id','=',kw.get("state_id"))])
            _logger.info(country)
            _logger.info(country_state)
            partner_id.update({
                "project_contribute": projects,
                "free_member": "1",
                "select_mentee": mentee_id.id,
                "country_id": country,
                "state_id": country_state,
                "city": kw.get("city"),
                "phone": kw.get("phone"),
                "member_type": "freemember",
                #  'image_1920':base64.b64encode(file.read()
            })
           


            

            # return request.render('http://207.154.229.160:8069/shop')
            return werkzeug.utils.redirect('/home-1')
        
        except UserError as e:
            qcontext['error'] = e.args[0]
       
        # response = request.render('auth_signup.signup', qcontext)
        response = request.render('auth_signup.signup', qcontext)

        response.headers['X-Frame-Options'] = 'DENY'
        return response
      

   
    
    
      
      
    #Custome forget password form Website side 
    
    @http.route('/register/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def custom_reset_password(self, *args, **kw):
        _logger.info("############# custom reset password form website ##############")
        _logger.info("Data:%s",kw)
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    phone = qcontext.get('phone')
                    # assert phone, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        phone, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(phone)
                    qcontext['message'] = _("An email has been sent with credentials to reset your password")
            except UserError as e:
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        response = request.render('register.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response  
    
    
        
        
        
    
    ###### This for Json [APP register Form]
    
    @http.route('/api/registerform', type='json', auth='public', website=False, sitemap=False)
    def registerForm(self, *args, **kw):
        _logger.info("############# Values form Json ###############")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("qcontext: %s",qcontext)

        try:
            self.do_signup(qcontext)
            # Send an account creation confirmation email
            if qcontext.get('token'):
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
                    
            _logger.info("________________________ Write Custom fileds_____________________________")

            partner_id = request.env['res.partner'].sudo().search([('email','=', kw.get('login'))], limit=1)
            res_user_id = request.env['res.users'].sudo().search([('login','=', kw.get('login'))], limit=1)
            _logger.info("res_user_id:%s",res_user_id)
            
            if res_user_id:
                res_user_id.partner_id.write({
                    "age": kw.get('age'),
                    "phone": kw.get('phone')
                })
                
                _logger.info("res_user: %s", res_user_id)
                _logger.info("res.partner: %s",  partner_id)
                    
                return {
                    "success": True,
                    "message": "Successfully registered"
                        
                        }

            
        except:
            return {
                "success": False,
                "message": "Something went wrong"
                     
            }
            
    
    

        
        
        

        
    
    
 
class CustomSignin(Home):
    
    
    @http.route('/web/signin', type='http',  auth='public', website=True)
    def signin_webform(self,  **kw):
        _logger.info("##########################")
        return http.request.render('register.sign_in_form')
        # return "Hello hkkkku" #request.render('register.sign_up_form',{})
    
    
    ### Website login
     
    @http.route('/membership_signin', type='http',website=True, auth='none')
    def membership_signin(self, redirect=None, **kw): 
        _logger.info("************** Membership  Sign in ****************")
        _logger.info("Data: %s",kw)
        _logger.info(request.params)
        email = kw.get("login")
        password = kw.get("password")
        
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('http://localhost:8069/shop')
        # response = request.render('web.login', values)

        response.headers['X-Frame-Options'] = 'DENY'
        return response
 
       
    
class AuthSignupHome(Home):
    
    # Website Reset Password 
    @http.route('/register/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def registerweb_auth_reset_password(self, *args, **kw):
        _logger.info("**************** custom Reset password  ***************")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("Qcontext:%s",qcontext)
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                _logger.info("*********** ***************")
                if qcontext.get('token'):
                    
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    _logger.info("*********** Searching phone number user***************")
                    
                    phone = qcontext.get('phone')
                    search_user = request.env['res.users'].sudo().search([('phone','=',phone)], limit=1)
                    partner_id = request.env['res.partner'].sudo().search([('phone','=',phone)], limit=1)
                    
                    _logger.info("Search_result:%s User Name: %s  phone: %s",search_user, search_user.name, search_user.phone)
                    # assert phone, _("No phone provided.")
                    _logger.info("search_user:%s",search_user)
                    response = request.render('register.confirm_reset_password',{"search_user":search_user})
                    phont_len = str(phone)
                    _logger.info(len(phont_len))
                    
                    
                    if  search_user.phone != phone:
                        qcontext['error'] = _("Invalid phone number")
                    elif  len(phont_len) == 10 and re.search("^[0-9]+$", phont_len) and search_user.phone == phone is not None:
                        _logger.info("************ 10 digit  right user*************") 
                        
                        size = 4;
                        verification = request.env['res.users'].sudo().generate_verification(size)
                        _logger.info("verification code: %s",verification)
                        phone = str(phone)
                        ## here sms_provider to sent the otp to the right user
                        try:
                            _logger.info("************  Tryyyyyyyyyyyy************")
                            phone = str(phone)
                            partner_id.write({
                                'verification_code':verification
                            })
                            
                            return response
                            
                            # _logger.info("############ %s",response)
                        except Exception as e: 
                            
                            _logger.info(f"Error Has Occured - %s",e)
                      
                        
                        return response
                    elif  len(phont_len) == 13:
                        _logger.info("************ 13 digits  right user*************") 
                        size = 4
                        verification = request.env['res.users'].sudo().generate_verification(size)
                        _logger.info("verification code: %s",verification)
                        phone = str(phone)
                        partner_id.write({
                                'verification_code':verification
                            })
                        ### here sms_provider to sent the otp to the right user
                        try:
                            _logger.info("************  Tryyyyyyyyyyyy************")
                            
                           
                            
                            partner_id.write({
                                'verification_code':verification
                            })
                            _logger.info("verification_code writed on res partner: %s",partner_id.verification_code)
                            return response
                            
                            # _logger.info("############ %s",response)
                        except Exception as e: 
                            
                            _logger.info(f"Error Has Occured - %s",e)
                      
                        return response
                    else:
                        qcontext['error'] = _("Incorrect phone number")
                   
            except UserError as e:
                
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        response = request.render('register.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    
    
    #confirm password reset with verification
    


    @http.route('/web/confirm_reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_confirm_reset_password(self, *args, **kw):
        _logger.info("**************** Confirm Reset password  ***************")
        _logger.info("Data: %s",kw)
        qcontext = self.get_auth_signup_qcontext()
        _logger.info("Qcontext:%s",qcontext)
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
               
                if qcontext.get('token'):
                    
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                         request.env.user.login, request.httprequest.remote_addr)
                    if kw.get('password') != kw.get("cpassword"):
                        qcontext['error'] = _("Password Not Match")

                    elif kw.get('password') == kw.get("cpassword"): # and search_user.phone == phone:
                        _logger.info("************ Correct password  match *************")
                        request.env['res.users'].sudo().confirm_reset_password(qcontext)
                        # qcontext['message'] = _("An email has been sent with credentials to reset your password")
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        # response = request.render('web.reset_password', qcontext)
        response = request.render('web.login')

        
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    
    
    
