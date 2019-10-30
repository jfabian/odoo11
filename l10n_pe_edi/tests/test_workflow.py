# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import tools
from odoo.exceptions import UserError

from .test_common import TestCommon


class TestWorkFlow(TestCommon):

    @tools.mute_logger('pysimplesoap.helpers')
    def test_01_draft_after_valid_or_with_ticket(self):
        """With this we prove that a document can't be set again in draft
        without the proper permisions and against the right workflow.
        """

        invoice = self.create_invoice(journal_id=self.journal_id)
        ticket = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.journal_bol)

        self.account_invoice.l10n_pe_edi_cron_send_valid_documents()
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(invoice.state, 'open')
        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'in_process')
        self.assertEqual(ticket.state, 'open')
        self.cancel_document([invoice, ticket], "Returned item")
        ticket.action_invoice_draft()
        invoice.action_invoice_draft()

        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'to_cancel')
        self.assertEqual(invoice.state, 'cancel')
        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'to_cancel')
        self.assertEqual(ticket.state, 'cancel')
        self.message_check(
            [invoice, ticket], "This invoice have been notified at least once")

    @tools.mute_logger('pysimplesoap.helpers')
    def test_02_rewrite_a_ticket_number(self):
        """Proving the paths to allow or deny the reassignation of a ticket
        number
        """

        ticket_a = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        ticket_b = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)

        wizard = self.env['ticket.update.wizard'].with_context({
            'active_id': ticket_a.id}).create({
                'l10n_pe_edi_ticket_numbers': '0000000'})
        with self.assertRaises(UserError):
            wizard.button_update_ticket_number()

        self.account_invoice.l10n_pe_edi_cron_send_valid_documents()

        compare = "%s: %s&gt;%s" % (
            "This document's ticket number for it's summary was updated from",
            ticket_a.l10n_pe_edi_ticket_number, '0000000')
        wizard = self.env['ticket.update.wizard'].with_context({
            'active_id': ticket_a.id}).create({
                'l10n_pe_edi_ticket_numbers': '0000000'})
        wizard.button_update_ticket_number()
        self.message_check([ticket_a, ticket_b], compare)

        # Now using the manual summary generator
        ticket_c = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        ticket_d = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)

        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        wizard = wizard_obj.create({'reference_date': self.today_date,
                                    'summary_type': 'rc'})
        wizard.generate_document()
        compare = "%s: %s&gt;%s" % (
            "This document's ticket number for it's summary was updated from",
            ticket_c.l10n_pe_edi_ticket_number or 'Without ticket', '1111111')
        wizard = self.env['ticket.update.wizard'].with_context({
            'active_id': ticket_c.id}).create({
                'l10n_pe_edi_ticket_numbers': '1111111'})
        wizard.button_update_ticket_number()
        self.message_check([ticket_c, ticket_d], compare)
