# coding: utf-8
# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Odoo Peruvian Localization Reports",
    "summary": """
        Electronic accounting reports
            - Sales report
            - Purchase report
            - Journal Items
    """,
    "version": "10.0.1.0.0",
    "author": "Vauxoo",
    "category": "Accounting",
    "website": "http://www.vauxoo.com",
    "license": 'LGPL-3',
    "depends": [
        "account_reports",
        "l10n_pe",
        "l10n_pe_edi",
    ],
    "data": [
        "data/account_financial_report_data.xml",
    ],
    'demo': [
        'demo/res_partners.xml',
    ],
    'qweb': [
        'static/src/xml/account_report_backend.xml',
    ],
    "installable": True,
    "auto_install": True,
}
