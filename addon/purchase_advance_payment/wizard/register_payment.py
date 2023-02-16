from odoo import models, fields, api, exceptions, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class AccountPurchaseWizard(models.TransientModel):
    _name = "advance.purchase.payment.wizard"

    tax_ids = fields.Many2many('account.tax', 'account_tax_default_rel', 'account_id', 'tax_id', string='Default Taxes')

    expense_account = fields.Many2many('account.account', string='Purchase Account')
    debit_account = fields.Many2one('account.account', string='Account')
    partner_id = fields.Many2one('res.partner', string='User', required=True)
    partner_bank_account_id = fields.Many2one('res.partner.bank', string="Recipient Bank Account",
                                              domain="['|', ('company_id', '=', False), ('company_id', '=', "
                                                     "company_id)]")
    journal_id = fields.Many2one('account.journal', string='Purchase Journal', required=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type')
    amount = fields.Monetary(string='Payment Amount', store=True)
    tax_amount = fields.Monetary(string='Tax Amount', readonly=True, store=True)
    withhold_amount = fields.Monetary(string='withhold Amount', store=True, readonly=True)
    total_amount = fields.Monetary(string='Total Amount', store=True, required=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    communication = fields.Char(string='Memo')
    # change_amount = fields.Float(string='Change Amount', default=0.0, readonly=True, compute='_n_advance_amount')
    advance_amount = fields.Float(string='Advance Amount', readonly=True, required=True, compute='_before_tax_amount')
    before_tax_amount = fields.Float(string='Amount Before Tax', required=True, store=True)
    non_taxable_amount = fields.Float(string='Non-taxable amount', store=True)
    bank_id = fields.Many2one('account.account', string='Bank Account',
                              domain="[ ('user_type_id.name', '=', 'Bank and Cash')]")
    withholding_account = fields.Many2one("account.account",
                                          string="Withholding Account", store=True, readonly=True)
    taxed_account = fields.Many2one("account.account", string="Vat Account", store=True, readonly=True)
    purchase_id = fields.Many2one('purchase.order', "Purchase")
    is_total = fields.Boolean(string="Is Total payment", default=False)
    fiscal_year = fields.Many2one('fiscal.year', string="Fiscal year", required=True)
    time_frame = fields.Many2one('reconciliation.time.fream', 'Time frame')

    @api.model
    def default_get(self, fields):
        print("default_get")
        res = super(AccountPurchaseWizard, self).default_get(fields)
        account_ids = self.env.context.get('active_ids', [])
        acc2 = self.env['account.move'].browse(account_ids[0])
        fy = acc2.fiscal_year.id
        tf = acc2.time_frame.id
        purchase = self.env['purchase.order'].search([('id', '=', acc2.purchase_id.id)])
        advance_amount = 0
        amount = 0
        for line in acc2.line_ids:
            advance_amount = advance_amount + line.credit
            if line.debit != 0:
                account_id = line.account_id
                amount = line.debit
        print("line.account_id", line.account_id,purchase.id)
        values=[]
        tax_id=[]
        tax_ids=[]
        withhold = 0.0
        vat = 0.0
        for order_line in purchase.order_line:
            if order_line.usage_id.account_id:
                acc = order_line.usage_id.account_id
            elif self.env['product.product'].search(
                    [('id', '=', order_line.product_id.id)]).property_account_expense_id:
                acc = self.env['product.product'].search([('id', '=', order_line.product_id.id)
                                                          ]).property_account_expense_id
            else:
                acc = self.env['product.product'].search([('id', '=', order_line.product_id.id)
                                                          ]).categ_id.property_account_expense_categ_id
            if not acc:
                if order_line.product_id.name:
                    raise ValidationError(_("expense account product " + order_line.product_id.name + " is empty"))
                else:
                    raise ValidationError(
                        _("expense account product is empty"))
            val = acc.id
            taxes = order_line.taxes_id
            for tax in taxes:
                if tax.amount < 0:
                    withhold += tax.amount * order_line.price_unit/ 100
                else:
                    vat += tax.amount * order_line.price_unit / 100
                tax_ids.append((tax.id))
            values.append((val))


        print('fy', fy)
        if purchase:
            res.update({'partner_id': purchase.user_id.partner_id.id,
                        'total_amount': purchase.amount_total,
                        'fiscal_year': fy,
                        'time_frame': tf,
                        # 'advance_amount': purchase.amount_untaxed,
                        'debit_account': account_id.id,
                        'expense_account': [(6,0, values)],
                        'tax_ids': [(6,0, tax_ids)],
                        'before_tax_amount': purchase.amount_untaxed,
                        'purchase_id': purchase.id,
                        "tax_amount": vat,
                        "withhold_amount": withhold,
                        })
            print("res", res)
        return res

    def post_advance_payment(self):
        print("print")
        seq = self.env['ir.sequence'].next_by_code('advance.purchase.payment.sequence')
        move_vals = [(0, 0, {
                    'name': self.debit_account.name,
                    'debit': 0.0,
                    'credit': self.total_amount,
                    'account_id': self.debit_account.id,
                    'partner_id': self.partner_id.id,
                    'exclude_from_invoice_tab': True,
                })]

        for order_line in self.purchase_id.order_line:
            if order_line.usage_id.account_id:
                acc = order_line.usage_id.account_id
            elif self.env['product.product'].search([('id', '=', order_line.product_id.id)]).property_account_expense_id:
                acc = self.env['product.product'].search([('id', '=', order_line.product_id.id)
                                                      ]).property_account_expense_id
            else:
                acc = self.env['product.product'].search([('id', '=', order_line.product_id.id)
                                                          ]).categ_id.property_account_expense_categ_id
            if not acc:
                if order_line.product_id.name:
                    raise ValidationError(_("expense account product " + order_line.product_id.name + " is empty"))
                else:
                    raise ValidationError(
                    _("expense account product is empty"))

            move_vals.append((0, 0, {
                                'name': order_line.product_id.name,
                                'debit': order_line.price_unit * order_line.product_uom_qty,
                                'credit': 0.0,
                                'account_id': acc.id,
                                'product_id': order_line.product_id.id,
                                'price_unit': order_line.price_unit,
                                'product_uom_id': order_line.product_uom.id,
                                'quantity': order_line.product_uom_qty,
                                'tax_ids': [(6, 0, order_line.taxes_id.ids)],
                                'partner_id': self.partner_id.id,
                                'exclude_from_invoice_tab': False,
                             }))


        inv_values = {
            'name': seq,
            'partner_id': self.partner_id.id,
            'ref': self.purchase_id.name,
            'journal_id': self.journal_id.id,
            'line_ids': move_vals,
            'state': 'draft',
            'fiscal_year': self.fiscal_year.id,
            'time_frame': self.time_frame.id,

        }
        print("inv_values", inv_values)
        move = self.env['account.move'].sudo().create(inv_values)
        account_ids = self.env.context.get('active_ids', [])
        acc = self.env['account.move'].browse(account_ids[0])
        acc.flag_2 = False
        account_ids = self.env.context.get('active_ids', [])
        acc = self.env['account.move'].browse(account_ids[0])
        accounts = self.env['account.move'].search([('purchase_id', '=', acc.purchase_id.id)])
        for account in accounts:
                    account.write({'account_move_id': move.id})
                    account.flag_2 = False

        return
