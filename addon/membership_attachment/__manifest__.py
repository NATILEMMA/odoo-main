# -*- coding: utf-8 -*-
{
    'name': "membership_attachment",

    'summary': """
        Membershib attachment""",

    'description': """
        This module is dedicated to be able to add members attachment
    """,

    'author': "Tria Company",
    'website': "http://triaplc.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Membership',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website', 'base', 'auth_signup_verify_email', 'membership', 'members_custom', 'member_dashboard', 'reconciliation'],

    # make the sequence to top
    'sequence': 0,
    'application': True,

    # always loaded
    'data': [
        'views/attachment_fields_modification_views.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
