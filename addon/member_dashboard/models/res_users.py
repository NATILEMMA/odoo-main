
import random
import string
import werkzeug.urls

from collections import defaultdict
from datetime import datetime, timedelta
from odoo import api, exceptions, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.users'
    

    def confirm_reset_password(self, login):
        """ retrieve the user corresponding to login (login or email),
            and reset their password
        """
        _logger.info(login)
        users = self.search([('login', '=', login['login'])])
        _logger.info("Users: %s",users)
        if not users:
            users = self.search([('email', '=', login['login'])])
        if len(users) == 1:
            partner = self.env['res.partner'].search([('id','=',users.partner_id.id)])
            users.update({
                'password': login['password']
            })
            partner.update({
                'member_password_verfiy': True
            })
        if len(users) != 1:
            raise Exception(_('Reset password: invalid password'))
        else:
            users = self.env['res.users'].sudo().search([('login', '=', login['login'])])
          
        return users
