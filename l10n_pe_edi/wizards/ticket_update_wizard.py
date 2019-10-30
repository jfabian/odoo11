# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class TicketUpdateWizard(models.TransientModel):
    """Update Ticket Number Wizard"""

    _name = "ticket.update.wizard"

    l10n_pe_edi_ticket_numbers = fields.Char(
            string='Ticket number', help='Assign a new ticket to the documents'
            'related to a summary or ticket')

    @api.multi
    def button_update_ticket_number(self):
        invoice_id = self.env.context.get('active_id', False)
        doc = self.env['account.invoice'].search(
        [('id', '=', invoice_id)])

        if not doc.l10n_pe_edi_summary_id:
            raise UserError("This document can't at the moment be assigned a "
            "ticket number manually because it hasn't a summary")

        documents = self.env['account.invoice'].search(
        [('l10n_pe_edi_ticket_number', '=', doc.l10n_pe_edi_ticket_number),
        ('l10n_pe_edi_summary_id', '=', doc.l10n_pe_edi_summary_id.id),
        ('date_invoice', '=', doc.date_invoice),
        ('l10n_pe_edi_pse_status', 'not in', ['valid','cancelled'])])

        msg = "%s: %s&gt;%s" % (
        _("This document's ticket number for it's summary was updated from"),
        doc.l10n_pe_edi_ticket_number or _('Without ticket'),
        self.l10n_pe_edi_ticket_numbers)

        for document in documents:
            document.message_post(body=msg, message_type='comment')
        documents.write({
        'l10n_pe_edi_ticket_number': self.l10n_pe_edi_ticket_numbers})
