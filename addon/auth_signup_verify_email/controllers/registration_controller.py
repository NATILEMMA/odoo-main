"""This file will handle registration webpage"""

from odoo import http
from odoo.http import request
import base64

class RegsistrationController(http.Controller):

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
                    return request.render('auth_signup_verify_email.registration_end')
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
                    return request.render('auth_signup_verify_email.registration_end')
                # elif values['membership_type'] == 'supporter':
                #     values['work_place'] = values['company_name']
                #     values.pop('company_name')
                #     values.pop('membership_type')
                #     request.env['supporter.members'].sudo().create(values)
                #     return request.render('auth_signup_verify_email.registration_end')                                       
            else:
                if values['membership_type'] == 'candidate':
                    values.pop('membership_type')
                    request.env['candidate.members'].sudo().create(values)
                    return request.render('auth_signup_verify_email.registration_end')
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
                    return request.render('auth_signup_verify_email.registration_end')
                # elif values['membership_type'] == 'supporter':
                #     values['work_place'] = values['company_name']
                #     values.pop('company_name')
                #     values.pop('membership_type')
                #     values.pop()
                #     request.env['supporter.members'].sudo().create(values)
                #     return request.render('auth_signup_verify_email.registration_end')   
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
