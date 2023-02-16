from odoo import http
from odoo.http import request, Response
import base64
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging

_logger = logging.getLogger(__name__)

class PortalAccountDetail(CustomerPortal):

    CustomerPortal.MANDATORY_BILLING_FIELDS.remove("street")
    CustomerPortal.MANDATORY_BILLING_FIELDS.remove("email")
    CustomerPortal.MANDATORY_BILLING_FIELDS.remove("country_id")
    CustomerPortal.OPTIONAL_BILLING_FIELDS.extend(["title",
                                                   "is_company",
                                                   "gender",
                                                   "date",
                                                   "employment_status",
                                                   "ethnicity",
                                                   "subcity_id",
                                                   "wereda_id",
                                                   "country_id",
                                                   "street",
                                                   "email"])

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        if post and request.httprequest.method == 'POST':
            for field in set(['subcity_id', 'title', 'wereda_id']) & set(post.keys()):
                try:
                    post[field] = int(post[field])
                except:
                    post[field] = False
            image_1920 = post.get('image_1920')
            date = post.get('date')
            gender = post.get('gender')
            ethnicity = post.get('ethnicity')
            employment_status = post.get('employment_status')
            title = post.get('title')
            subcity_id = post.get('subcity_id')
            wereda_id = post.get('wereda_id')
            if image_1920:
                image_1920 = image_1920.read()
                image_1920 = base64.b64encode(image_1920)
                request.env.user.partner_id.sudo().write({
                    'image_1920': image_1920,
                    'date': date,
                    'gender': gender,
                    'ethnicity': ethnicity,
                    'employment_status': employment_status,
                    'title': title,
                    'subcity_id': subcity_id,
                    'wereda_id': wereda_id
                })
            post.pop('image_1920')
        titles = request.env['res.partner.title'].sudo().search([])
        subcities = request.env['membership.handlers.parent'].sudo().search([])
        weredas = request.env['membership.handlers.branch'].sudo().search([])
        req = super().account(redirect=redirect, **post)
        # The qcontext will hold contexts to be added to the template.
        # It can be edited from a Response instance(object)
        req.qcontext.update({'titles': titles,
                             'subcities': subcities,
                             'weredas': weredas})
        return req
