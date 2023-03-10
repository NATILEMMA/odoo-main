# Copyright 2015 Antiun Ingeniería, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Verify email at signup",
    "summary": "Force uninvited users to use a good email for signup",
    "version": "13.0.1.0.2",
    "category": "Authentication",
    "website": "https://github.com/OCA/server-auth",
    "author": "Antiun Ingeniería S.L., "
    "Tecnativa, "
    "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "sequence": 0,
    "application": True,
    "depends": ["auth_signup", "hr", "website", "snailmail_account"],
    "external_dependencies": {"python": ["lxml", "email_validator"]},
    "data": [
        "views/signup.xml",
        'views/account_detail.xml',
        'views/registration_form.xml'
    ],
    "installable": True,
}
