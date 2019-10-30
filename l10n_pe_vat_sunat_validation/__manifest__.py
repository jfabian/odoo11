# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Validation RUC SUNAT ",
    "version": "10.0.1.0.0",
    "author": "Edgard Pimentel, Vauxoo",
    "category": "Localization\\Peru",
    "website": "http://www.vauxoo.com/",
    "license": "",
    "depends": [
        "base_vat",
        "l10n_pe_toponyms",
    ],
    "data": [
        "data/ir_config_parameter.xml",
    ],
    "demo": [
        "demo/ir_config_parameter.xml",
    ],
    'external_dependencies': {
        'python': ['requests_mock'],
    },
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False
}
