
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
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
from odoo.osv.expression import OR



_logger = logging.getLogger(__name__)
import string
# import africastalking



class WebRegisteration(AuthSignupHome):
    
    
    @http.route('/success', type='http',  auth='public', website=True)
    def reset_password(self,  **kw):
        return http.request.redirect('/shop')


    @http.route('/', type='http',  auth='public', website=True)
    def home(self,  **kw):
        _logger.info("@@@@@@@@@@@@")
        company = request.env['res.company'].sudo().search([])
        return http.request.render('AADBO_website.Home')
        
    @http.route('/home', type='http',  auth='public', website=True)
    def home1(self,  **kw):
        _logger.info("@@@@@@@@@@@@")
        company = request.env['res.company'].sudo().search([])
        return http.request.render('AADBO_website.Home')
        
    
    
    @http.route('/about-us', type='http',  auth='public', website=True)
    def abour(self,  **kw):
        company = request.env['res.company'].sudo().search([])
        return http.request.render('AADBO_website.about_us')
        
    
    @http.route('/registration', type='http', auth='public', website=True)
    def register(self, **post):
        """This function will create supporters from portal"""
        if post and request.httprequest.method == 'POST':
            values = {}
            values.update(post)
            for field in set(['subcity_id', 'wereda_id', 'region', 'education_level']) & set(values.keys()):
                try:
                    values[field] = int(values[field])
                except:
                    values[field] = False
            name = values['first_name'] + ' ' + values['fathers_name'] + ' ' + values['grandfathers_name']
            values['name'] = name
            values.pop('first_name') 
            values.pop('fathers_name')
            values.pop('grandfathers_name')
            if values['image_1920']:
                values['image_1920'] = values['image_1920'].read()
                values['image_1920'] = base64.b64encode(values['image_1920'])
                if values['membership_type'] == 'candidate':
                    values.pop('membership_type')
                    request.env['candidate.members'].sudo().create(values)
                    return request.render('AADBO_website.registration_end')
                elif values['membership_type'] == 'league':
                    values['is_league'] = True
                    values['is_member'] = False
                    values['is_leader'] = False
                    values['was_league'] = True
                    values.pop('membership_type')
                    if values['company_name'] and values['position']:
                        values['work_experience_ids'] = [(
                            0,
                            0, 
                            {
                                'name': values['position'],
                                'place_of_work': values['company_name'],
                                'current_job': True
                            }
                        )]
                        values.pop('company_name')
                        values.pop('position')
                    else:
                        values.pop('company_name')
                        values.pop('position')
                    request.env['res.partner'].sudo().create(values)
                    return request.render('AADBO_website.registration_end')
                # elif values['membership_type'] == 'supporter':
                #     values['work_place'] = values['company_name']
                #     values.pop('company_name')
                #     values.pop('membership_type')
                #     request.env['supporter.members'].sudo().create(values)
                #     return request.render('AADBO_website.registration_end')                                       
            else:
                if values['membership_type'] == 'candidate':
                    values.pop('membership_type')
                    request.env['candidate.members'].sudo().create(values)
                    return request.render('AADBO_website.registration_end')
                elif values['membership_type'] == 'league':
                    values['is_league'] = True
                    values['is_member'] = False
                    values['is_leader'] = False
                    values['was_league'] = True
                    values.pop('membership_type')
                    if values['company_name'] and values['position']:
                        values['work_experience_ids'] = [(
                            0,
                            0, 
                            {
                                'name': values['position'],
                                'place_of_work': values['company_name'],
                                'current_job': True
                            }
                        )]
                        values.pop('company_name')
                        values.pop('position')
                    else:
                        values.pop('company_name')
                        values.pop('position')
                    request.env['res.partner'].sudo().create(values)
                    return request.render('AADBO_website.registration_end')
                # elif values['membership_type'] == 'supporter':
                #     values['work_place'] = values['company_name']
                #     values.pop('company_name')
                #     values.pop('membership_type')
                #     values.pop()
                #     request.env['supporter.members'].sudo().create(values)
                #     return request.render('AADBO_website.registration_end')   
        cities = request.env['res.country.state'].sudo().search([('country_id', '=', 69)])
        ed_levels = request.env['res.edlevel'].sudo().search([])
        subcities = request.env['membership.handlers.parent'].sudo().search([])
        weredas = request.env['membership.handlers.branch'].sudo().search([])
        return request.render("AADBO_website.registration_form", {
                                                                              'ed_levels': ed_levels,
                                                                              'cities': cities,
                                                                              'subcities': subcities,
                                                                              'weredas': weredas
                                                                            })
