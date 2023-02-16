"""This file will handle complainct webpage"""

from odoo import http
from odoo.http import request

class ComplaintController(http.Controller):

    @http.route('/complaint/<int:id>/edit', type='http', auth='user', website='True')
    def edit_customize(self, id, **kwargs):
        """This function will edit the complaint on the form"""
        request.redirect('/my/create_complaint')
        complaint = request.env['member.complaint'].sudo().search([('id', '=', id)])
#        complaint_category = request.env['complaint.category'].sudo().search([])
        perpertrators = request.env['hr.employee'].sudo().search([])
        return request.render("members_custom.complaint_form",
        {
            'complaint': complaint,
#            'complaint_category': complaint_category,
            'perpertrators': perpertrators
        })

    @http.route('/complaint/<int:id>/delete', type='http', auth='user', website='True')
    def delete_complaint(self, id, **kwargs):
        """This function will delete the complaint on the from database"""
        complaint = request.env['member.complaint'].sudo().search([('id', '=', id)])
        complaint.unlink()
        return request.redirect('/my/complaint')

    @http.route('/my/complaint', type='http', auth='user', website='True', methods=['GET'])
    def complaint_data(self, **kwargs):
        """This function will handle the displaying for complaints"""
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id
#        partner = request.env.user.partner_id
        complaint = request.env['member.complaint'].sudo().search([('victim_id', '=', user.id)])
        return request.render("members_custom.complaint_list", {'record': complaint})


    @http.route('/my/create_complaint', type='http', auth='user', website='True')
    def complaint_saving(self, **kwargs):
        """This function will access and populate a new form for complaint"""
#        complaint_category = request.env['complaint.category'].sudo().search([])
        perpertrators = request.env['hr.employee'].sudo().search([])
        return request.render("members_custom.complaint_form",
        {
#            'complaint': {'id': None, 'subject': None, 'circumstances': None, 'complaint_category': {'id': None}, 'perpertrators': None},
#            'complaint_category': complaint_category,
             'complaint': {'id': None, 'subject': None, 'circumstances': None, 'perpertrators': None},
             'perpertrators': perpertrators
        })

    @http.route('/add_complaint', type='http', auth='user', website='True')
    def complaint_entry(self, **kwargs):
        """This function will handle the entry and editing of a new complaint"""
        # The following statement will get a list of ids from the selected values in form
        # [(6, 0, ids)] also means create a record for  many2many and one2many
        perps = request.httprequest.form.getlist('perpertrators')
        user = request.env['res.users'].sudo().browse(request.session.uid).partner_id
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
#            'complaint_category': kwargs.get('complaint_category'),
            'state': 'updated',
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
          request.env['member.complaint'].sudo().create({
            'victim_id': user.id,
            'subject': kwargs.get('subject'),
            'circumstances': kwargs.get('circumstances'),
#            'complaint_category': kwargs.get('complaint_category'),
            'perpertrators': [
              (
                6,
                0,
                perps
              )
            ]
          })
          return request.render("members_custom.complaint_end", {})
