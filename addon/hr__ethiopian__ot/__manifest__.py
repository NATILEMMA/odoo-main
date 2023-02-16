# -*- coding: utf-8 -*-
{
    'name': "Ethiopia-Overtime",

    'summary': """
        over time """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Elnet Technologies",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr', 'hr_contract','hr_attendance', 'hr_holidays','hr_payroll_community', 'mail'],

    # always loaded
    'data': [
        'security/ot_security.xml',
        'views/ot_type_rate.xml',
        'views/hr_contract.xml',
        'views/ot_request.xml',
        'views/hr_payslip.xml',
        'security/ir.model.access.csv',

    ],
    # only loaded in demonstration mode
    'license': 'AGPL-3',
    'demo': [
        'demo/demo.xml',
    ],
}
