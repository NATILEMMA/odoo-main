# -*- coding: utf-8 -*-
{
    'name': "Bid Document",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': [],

    # always loaded
    'data': [
        'data/seq.xml',
        'security/ir.model.access.csv',
        'views/bid_document_view.xml',
        'report/report_bid_document.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
