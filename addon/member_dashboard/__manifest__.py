
{
    'name': 'Membership Dashboard',
    'version': '1.0',
    'category': 'Extra-tools',
    'description': "",
    "author": " ",
    'depends': ['base','web','project','website_event'],
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/membership_template.xml',
        'views/partner_views.xml'
    ],
    #      'assets': {
    #     'web.assets_frontend': [
    #         'member_dashboard/static/src/js/custom.js',
    #         '/member_dashboard/static/src/js/vendor.bundle.base.js',
    #         '/member_dashboard/static/src/js/Chart.min.js',
    # ]},

    'css': ['static/src/css/customstyle.css'],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
