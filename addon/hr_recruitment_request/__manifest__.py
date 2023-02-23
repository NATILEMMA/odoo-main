# -*- coding: utf-8 -*-
{
    'name': "recruitment Request Module",
    'author': "My Company",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr','hr_recruitment'],

    # always loaded
    'data': [
        'data/seq.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_recruitment_request_view.xml',
        'report/report.xml',
        'report/report_application_request.xml',
    ],
    # only loaded in demonstration mode
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
