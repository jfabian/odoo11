# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo
# Copyright (C) 2016 Akretion (http://www.akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductUom(models.Model):
    _inherit = 'product.uom'

    l10n_pe_unece_code = fields.Char(
        string='UNECE Code',
        help="Standard nomenclature of the United Nations Economic "
        "Commission for Europe (UNECE).")
