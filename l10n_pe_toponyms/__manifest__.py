# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'l10n_pe Geopolitical Distribution',
    'version': '10.0.1.0.0',
    'category': 'Localization/Peru',
    'depends': [
        'sales_team',
    ],
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    "license": 'LGPL-3',
    'data': [
        'security/l10n_pe_security.xml',
        'security/ir.model.access.csv',
        'data/res_state_data.xml',
        'data/res_country_data.xml',
        'views/res_country_view.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False
}
