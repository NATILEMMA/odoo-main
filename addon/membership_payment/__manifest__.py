# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    # Module Information
    'name': 'membership payment',
    'category': 'Managing vehicles and contracts',
    'sequence': 1,
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    'summary': """handel membership payment.
    """,
    'description': """handel membership payment.
    """,
    'author': 'Amen mesfin',

    'depends': ['members_custom'],
    # Data
    'data': [
        'views/sub_payment.xml',
        'views/city_pay.xml',
        'views/main_pay.xml',
        'data/subcity_sequence.xml',
        'security/ir.model.access.csv'
    ],
    # Technical
    'installable': True,
    'application': True,
}
