# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import re

from odoo import api, fields, models


class InvoiceCancelWizard(models.TransientModel):
    """Invoice Cancel Wizard"""

    _name = "invoice.cancel.wizard"

    l10n_pe_cancel_reason = fields.Char(
        string='Cancel Reason', help='Reason to cancel this entry',
        required=True,)

    l10n_pe_cancel_reason_strip = fields.Char(
        compute='_compute_l10n_pe_cancel_reason_strip',
        help='Field to strip unwanted characters',
        string='Cancel reason should not be empty or have symbols or be less '
        'than 3 characters', required=True)

    @api.multi
    def button_cancel_reason(self):
        invoice_id = self.env.context.get('active_id', False)
        invoice = self.env['account.invoice'].browse(invoice_id)
        invoice.write(
            {'l10n_pe_cancel_reason': self.l10n_pe_cancel_reason})
        invoice.action_invoice_cancel()

    @api.multi
    @api.depends('l10n_pe_cancel_reason')
    def _compute_l10n_pe_cancel_reason_strip(self):
        if self.l10n_pe_cancel_reason:
            self.l10n_pe_cancel_reason_strip = re.sub(
                r'[^a-zA-Z\d\s]|\A[a-zA-Z\d]{1,2}[^a-zA-Z\d]*\Z',
                '', self.l10n_pe_cancel_reason.strip())
            self.l10n_pe_cancel_reason = self.l10n_pe_cancel_reason_strip
