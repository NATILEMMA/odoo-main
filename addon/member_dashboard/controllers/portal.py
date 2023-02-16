# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import json
import math
import re

from werkzeug import urls

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
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
from odoo.osv.expression import OR
from odoo import fields, http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.controllers.main import QueryURL
from odoo.http import request
from odoo.tools.misc import get_lang
from odoo.addons.portal.controllers.portal import CustomerPortal


from odoo import fields as odoo_fields, http, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError
from odoo.http import content_disposition, Controller, request, route
from odoo.tools import consteq
import logging
_logger = logging.getLogger(__name__)


class CustomerPortal(Controller):

  
    def _prepare_portal_layout_values(self):
        """Values for /my/* templates rendering.

        Does not include the record counts.
        """
        # get customer sales rep
        sales_user = False
        partner = request.env.user.partner_id
        partners = request.env['res.partner'].sudo().search([('id','=', partner.id)], limit=1)
        user = request.env['res.users'].sudo().search([('partner_id','=', partner.id)], limit=1)
        _logger.info(user)
        _logger.info(partners)
        _logger.info(partners.member_password_verfiy)
        _logger.info(user.has_group('base.group_portal'))
        _logger.info(user.env.ref('base.group_portal').id)

        if partner.user_id and not partner.user_id._is_public():
            sales_user = partner.user_id

        return {
            'user': user, 
            'portal_user': user.has_group('base.group_portal'),
            'portal_user_verfiy': partners.member_password_verfiy,
            'sales_user': sales_user,
            'page_name': 'home',
            'archive_groups': [],
        }

    def _prepare_home_portal_values(self):
        """Values for /my & /my/home routes template rendering.

        Includes the record count for the displayed badges.
        """
        return self._prepare_portal_layout_values()

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self,  page=1, **searches):
        _logger.info('///MY')
        _logger.info(searches)
        values = self._prepare_home_portal_values()
        _logger.info(values)

        if values['portal_user'] ==  True and values['portal_user_verfiy'] == False:

            return request.render("member_dashboard.confirm_reset_password", values)
        else:
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
