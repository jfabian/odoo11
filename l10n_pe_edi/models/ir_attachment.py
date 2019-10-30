# -*- coding: utf-8 -*-
# Copyright 2017 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    l10n_pe_edi_sunat_file = fields.Boolean("SUNAT Document", default=False,
                                            copy=False)
