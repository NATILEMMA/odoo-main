from odoo import fields, models


class InstutionType(models.Model):
    _name = 'hr.employee.instution.type'
    _description = 'hr employee instution type'
    

    name = fields.Char(string='Instution Type', required=True, help="Instution Type Name")



class ResPartner(models.Model):
    _inherit = 'res.partner'
    instution_type_id = fields.Many2one('hr.employee.instution.type', string="Instution Type",
                              required=True)


