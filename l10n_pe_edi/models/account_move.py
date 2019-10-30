# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, api, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self):
        """ Use debit note sequence if defined
        If the current document is actually a debit note and the journal
        related has a debit sequence then use that one, or use the regular one
        in counter case
        """
        invoice = self.env.context.get('invoice', False)
        if not invoice:
            return super(AccountMove, self).post()
        new_name = False
        if invoice and invoice.move_name and invoice.move_name != '/':
            new_name = invoice.move_name
        for move in self.filtered(lambda r: r.name == '/'):
            journal = move.journal_id
            sequence = journal.charge_sequence and journal.charge_sequence_id \
                or journal.sequence_id
            if not sequence:
                raise UserError(_('Please define a sequence '
                                  'for the debit notes'))
            if (not new_name and invoice.type == 'out_invoice' and
                    invoice.refund_invoice_id):
                new_name = sequence.with_context(
                    ir_sequence_date=move.date).next_by_id()

            if new_name:
                move.name = new_name
        return super(AccountMove, self).post()
