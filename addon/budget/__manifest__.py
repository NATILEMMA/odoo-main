
{
    'name': 'Budget Planning & Management',
    'version': '13.0.1.1.0',
    'summary': """ Budget Planning And Management for Odoo 13 """,
    'description': """ This module allows accountants to manage analytic and budgets.

     Once the Budgets are defined (in Accounting/Accounting/Budgets), the Project Managers
     can set the planned amount on each Analytic Account.
     
     The accountant has the possibility to see the total of amount planned for each
     Budget in order to ensure the total planned is not greater/lower than what he
     planned for this Budget. Each list of record can also be switched to a graphical
     view of it.
     
     Three reports are available:

     1. The first is available from a list of Budgets. It gives the spreading, for
     these Budgets, of the Analytic Accounts.
     2. The second is a summary of the previous one, it only gives the spreading,
     for the selected Budgets, of the Analytic Accounts.
     3. The last one is available from the Analytic Chart of Accounts. It gives
    """,
    'category': 'Accounting',
    'sequence': 100,
    'author': 'mes',
    'company': 'mes',
    'maintainer': 'mes',
    'depends': ['base',  'mail',
        'portal','account','project', 'base_accounting_kit','hr_expense','reconciliation'],
    'data': [
        'data/data.xml',
        'security/budget_group_rules.xml',
        'security/account_budget_security.xml',
        'security/ir.model.access.csv',
        'views/account_analytic_account_views.xml',
        'views/account_budget_views.xml',
        'views/budget_planning.xml',

        
        
        
    ],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
