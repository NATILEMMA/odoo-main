# Copyright (C) 2021 Sunflower IT (<http://www.sunflowerweb.nl>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    description = fields.Text(string="Description")
