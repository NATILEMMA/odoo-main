from odoo import api, fields, models


class ResConfigSettings_2(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_account = fields.Many2one("account.account", string="Default advance purchase Account")

    @api.model
    def get_values(self):
        print("get_values")
        res = super(ResConfigSettings_2, self).get_values()
        # purchase_account = (
        #     self.env['ir.config_parameter'].sudo().get_param('purchase_advance_payment.purchase_account'))
        # #if purchase_account[16] != ')':
        # if purchase_account[17] == ',':
        #         num = int(purchase_account[16])
        # elif purchase_account[18] == ',':
        #         num=int(purchase_account[16]+purchase_account[17])
        # else:
        #         num = int(purchase_account[16] + purchase_account[17] + purchase_account[18])
        #     res.update(
        #         purchase_account = num

        #         )
        return res

    def set_values(self):
        print("set_values")
        super(ResConfigSettings_2, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        field2 = self.purchase_account
        param.set_param('purchase_advance_payment.purchase_account', field2)

