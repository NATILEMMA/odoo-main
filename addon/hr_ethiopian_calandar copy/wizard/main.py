import random
import string
import werkzeug.urls

from collections import defaultdict
from datetime import datetime, timedelta
from odoo import api, exceptions, fields, models, _
from ethiopian_date import EthiopianDateConverter
import logging
_logger = logging.getLogger(__name__)

class MyMeeting(models.TransientModel):
    _name = 'my.meeting.wizard'

    name = fields.Char('Name')


    # @api.model
    # def