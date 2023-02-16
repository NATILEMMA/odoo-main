
{
    'name': "Fund Management",
    'summary': """
       Fund Management.
       """,

    'description': """
        This modules provides  features - 
       -> Fund Collection\n
       -> Fund Allocation\n
       -> Fund Distribution\n
       -> Fund Control\n
    """,

    'author': "",
    'website': "",
    'sequence': 101,

    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base_accounting_kit','hr',  'mail',
        'portal','budget','base','project'],
    'data': [
        'data/data.xml',
        'security/fund_group_rules.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
        'views/inherit_employee_view.xml',
        'views/fund_view_menu.xml',
        'views/account_analytic_account_views.xml',
        'views/account_fund_views.xml',
    ],
   
    'images': ['static/description/icon2.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}