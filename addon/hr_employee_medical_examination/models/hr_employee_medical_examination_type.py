# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ExaminationType(models.Model):
    _name = 'hr.employee.medical.examination.type'
    _description = 'employee medical examination type'
    _rec_name = "complete_name"

    parent_id = fields.Many2one(comodel_name="hr.employee.medical.examination.type", string="Parent Type")
    child_ids = fields.One2many(comodel_name="hr.employee.medical.examination.type", inverse_name="parent_id", string="Subtypes")
    name = fields.Char(string='Examination Type', required=True, help="Name")
    complete_name = fields.Char(
        string="Complete Name", compute="_compute_complete_name", store=True
    )


    @api.constrains("parent_id")
    def check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_("You cannot create recursive examination type."))
        

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        for examination_type in self:
            if examination_type.parent_id:
                examination_type.complete_name = "{} / {}".format(
                    examination_type.parent_id.complete_name, examination_type.name
                )
            else:
                examination_type.complete_name = examination_type.name




