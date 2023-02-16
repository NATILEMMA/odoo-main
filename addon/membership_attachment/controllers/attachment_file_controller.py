""This file will handle Attachment webpage"""

from odoo import http
from odoo.http import request
import base64

class AttachmentController(http.Controller):

   @http.route('/my/add_attachments', type='http', auth='user', website='True')
   def add_attachments(self, **kwargs):
       """This function will attach files with member"""
       partner = request.env.user.partner_id
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
       return request.render("membership_attachment.attachment_form", 
        {
            'object': {'id': None, 'description': None, 'attachment_type': {'id': None, 'name': None}},
            'attachment_type': attachment_type,
            'attachment': attachment,
            'root': '/my/add_attachments'
        })


   @http.route('/my/add_attachments/<int:id>/<string:action>', auth='public', website=True)
   def attachment_action(self, id, action, **kw):
    rec = request.env['ir.attachment'].sudo().search([('id', '=', id)])
    if action == 'edit':
       partner = request.env.user.partner_id
       attachment_type = request.env['attachment.type'].sudo().search([])
       attachment = request.env['ir.attachment'].sudo().search([('res_id', '=', partner.id)])
       return http.request.render('membership_attachment.attachment_form', {
           'object': rec,
            'root': '/my/add_attachments',
           'attachment_type': attachment_type,
           'attachment': attachment
       })
    if action == 'delete':
       rec.unlink()
       return request.redirect('/my/add_attachments')


