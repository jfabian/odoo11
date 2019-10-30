# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.depends('name')
    def _compute_tax_type_code(self):
        """ Based on tax defined will return a pai.
        :return: The code based on sunat calalog no 15 (https://goo.gl/rGedAU)
         * '1000' - 'VAT'
           '2000' - 'EXC'
           '9999' - 'OTH'
        """
        code = ''
        if self.name == 'IGV 18% Venta':
            code = '1000'
        self.l10n_pe_tax_type_code = code

    l10n_pe_tax_type_code = fields.Selection([
        ('1000', 'VAT'),
        ('2000', 'EXC'),
        ('9999', 'OTH')
    ], compute="_compute_tax_type_code", default="1000")
