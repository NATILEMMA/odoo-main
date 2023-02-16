# -*- coding: utf-8 -*-
# from odoo import http


# class HrEthiopianOt(http.Controller):
#     @http.route('/hr__ethiopian__ot/hr__ethiopian__ot/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr__ethiopian__ot/hr__ethiopian__ot/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr__ethiopian__ot.listing', {
#             'root': '/hr__ethiopian__ot/hr__ethiopian__ot',
#             'objects': http.request.env['hr__ethiopian__ot.hr__ethiopian__ot'].search([]),
#         })

#     @http.route('/hr__ethiopian__ot/hr__ethiopian__ot/objects/<model("hr__ethiopian__ot.hr__ethiopian__ot"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr__ethiopian__ot.object', {
#             'object': obj
#         })
