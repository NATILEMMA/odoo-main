# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'biding Custom Module',
    'version': '0.1',
    'category': 'Operations/Purchase',
    'description': "",
    'depends': ['purchase_request'],
    'demo': [],
    'data': [
        'views/purchase_requsition.xml',
        'views/vendor_document.xml',
        'views/vendor.xml',
        'views/product_document.xml',
        'views/product.xml',
        'security/ir.model.access.csv',
        'report/tendor_result_view.xml',
        'report/tendor_results.xml',
        'report/bidding_document.xml'
    ],
}
