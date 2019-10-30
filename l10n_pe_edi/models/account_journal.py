# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models

from .account_invoice import L10N_PE_EDI_JOURNAL_CODES


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    charge_sequence_id = fields.Many2one(
        'ir.sequence', string='Debit Entry Sequence',
        help="This field contains the information related to the numbering of "
        "the debit note entries of this journal.", copy=False)
    charge_sequence = fields.Boolean(
        string='Dedicated Debit Note Sequence',
        help="Check this box if you don't want to share the same sequence for "
        "invoices and debit note made from this journal", default=False)

    @api.multi
    def _get_sequence_prefix(self, code, refund=False):
        if code in L10N_PE_EDI_JOURNAL_CODES:
            return code.upper() + '-'
        return super(AccountJournal,
                     self)._get_sequence_prefix(code, refund)
