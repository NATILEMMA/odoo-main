
{
    'name': 'Bank Reconciliation',
    'version': '13.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Replacing default bank statement reconciliation method by traditional way',
    'description': """Replacing default bank statement reconciliation method by traditional way""",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/bank_reconciltion.xml',
        'wizard/closing.xml',
        'wizard/open.xml',
        'views/time_frame.xml',
        'views/account_move_line_view.xml',
        'views/account_move_view.xml',
        'views/fiscal_year.xml',
        'views/account.xml',



    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
}
