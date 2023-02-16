# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Request',
    'version': '1.0',
    'category': 'Purchases',
    'author':'tung.tung11191@gmail.com',
    'description': """
Use Purchase Request module for requesting product.
    """,
    'summary': 'Create purchase request',
    'website': 'http://sprogroup.com',
    'images': ['static/description/icon.jpg'],
    'data': [
        'security/purchase_request_security.xml',
        'security/ir.model.access.csv',
        'data/purchase_request_data.xml',
        'report/report_views.xml',
        'report/test_report.xml',
        'views/purchase_request_view.xml',
        'views/purchase_order.xml',
        'views/config.xml',
        'views/p_o.xml',
    ],
    'depends': ['base','mail','purchase_requisition','hr','hr_expense'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'sequence': 105,
    'license': 'AGPL-3',
}
