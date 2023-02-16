# ©  2020 Deltatech
# See README.rst file on addons root folder for license details
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import AccessError, UserError, ValidationError

class MergeRequisition(models.TransientModel):
    _name = "merge.requisition.wizard"
    _description = "Merge Statement Wizard"

    requisition_id_many = fields.Many2one('purchase.requisition', required=True, string='New Purchase Agreement')
    requisition_id_many_2 = fields.Many2many('purchase.requisition', string='merged Purchase Agreement')

    @api.model
    def default_get(self, fields_list):
        res = super(MergeRequisition, self).default_get(fields_list)
        active_ids = self.env.context.get("active_ids")
        print("active_ids",active_ids)
        line_2=[]
        for line in active_ids:
            line_2.append(line)
        res.update({"requisition_id_many_2": [(6, 0, line_2)]})

        return res

    def merge(self):
        for tender in self.requisition_id_many_2:
           # if tender.state != 'draft':
           #    raise ValidationError(_("you can only merge draft state agreement"))
           acc = self.env['purchase.requisition'].search([('id', '=', tender.id)])
           acc_2 = self.env['purchase.requisition'].search([('id', '=', self.requisition_id_many.id)])
           acc_3 = self.env['purchase.requisition.line'].search([('requisition_id', '=', acc_2.id)])


           if tender.id != self.requisition_id_many.id:
               for line in acc.line_ids:
                    acc_3.create({"requisition_id": acc_2.id,"product_id": line.product_id.id, "product_qty": line.product_qty,
                                             "product_uom_id": line.product_uom_id.id, "price_unit": line.price_unit})
               acc.update({"state": "done"})
        self.requisition_id_many.action_compute()
        return



