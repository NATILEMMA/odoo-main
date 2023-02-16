# -*- coding: utf-8 -*-
# Copyright 2015 Omar Castiñeira, Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Advance Payment",
    "version": "10.0.1.0.0",
    "author": "Comunitea",
    'website': 'www.comunitea.com',
    "category": "Purchases",
    "description": """Allow to add advance payments on purchases and then use its on invoices""",
    "depends": ["purchase", "account"],
    "data": [
             'data/purchase_advance_sequence.xml',
             'data/purchase_advance_payment_sequence.xml',
             'wizard/purchase_advance_payment_wzd_view.xml',
             'views/purchase_view.xml',
             'views/payment_view.xml',
             'wizard/register_payment.xml',
             'views/register_payment.xml',
             "views/compute.xml",

             'security/ir.model.access.csv',
              'views/res_config.xml',
              "report/external_report_inherited.xml",
    ],
    "installable": True,
}
