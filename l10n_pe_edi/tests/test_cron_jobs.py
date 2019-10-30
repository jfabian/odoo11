# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import timedelta
from os.path import splitext

import mock
from lxml.etree import fromstring

from odoo import tools

from .test_common import TestCommon


class TestCronJobs(TestCommon):
    def setUp(self):
        super(TestCronJobs, self).setUp()
        today = self.env['l10n_pe_edi.certificate'].get_pe_current_datetime()
        yesterday = today - timedelta(days=1)
        self.yesterday_date = yesterday.date().strftime(
            tools.DEFAULT_SERVER_DATE_FORMAT)
        self.today_date = today.date().strftime(
            tools.DEFAULT_SERVER_DATE_FORMAT)

    @tools.mute_logger('pysimplesoap.helpers')
    def test_01_voided_cron_job_different_dates(self):
        """In this test we include all the posible cases for the cron to
        encounter while searching for the voided summary:
        - The documents can't be of the same day
        - The documents can't be from more than 7 days after it's validation
        - Invoices without CDR are not allowed
        """
        invoice_today = self.create_and_send(self.journal_id)
        invoice_1 = self.create_and_send(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 1))
        invoice_7 = self.create_and_send(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 7))
        invoice_8 = self.create_and_send(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 8))

        invoice_no_cdr = self.create_invoice(journal_id=self.journal_id)
        invoice_no_cdr_1 = self.create_invoice(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 1))
        invoice_no_cdr_7 = self.create_invoice(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 7))
        invoice_no_cdr_8 = self.create_invoice(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 8))

        # This are particular cases, because this documents doesn't have CDR
        invoice_no_cdr.l10n_pe_edi_cdr_date = False
        invoice_no_cdr_1.l10n_pe_edi_cdr_date = False
        invoice_no_cdr_7.l10n_pe_edi_cdr_date = False
        invoice_no_cdr_8.l10n_pe_edi_cdr_date = False

        ticket_today = self.create_and_send(
            journal_id=self.journal_bol, partner=self.partner_bol)
        ticket_1 = self.create_and_send(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 1))
        ticket_7 = self.create_and_send(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 7))
        ticket_8 = self.create_and_send(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 8))

        ticket_no_cdr = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        ticket_no_cdr_1 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 1))
        ticket_no_cdr_7 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 7))
        ticket_no_cdr_8 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 8))

        # This are particular cases, because this documents doesn't have CDR
        ticket_no_cdr.l10n_pe_edi_cdr_date = False
        ticket_no_cdr_1.l10n_pe_edi_cdr_date = False
        ticket_no_cdr_7.l10n_pe_edi_cdr_date = False
        ticket_no_cdr_8.l10n_pe_edi_cdr_date = False

        # This 2 groups are not going to be cancelled
        invoice_open = self.create_invoice(journal_id=self.journal_id)
        invoice_open_1 = self.create_invoice(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 1))
        invoice_open_no_cdr = self.create_invoice(journal_id=self.journal_id)
        invoice_open_no_cdr_1 = self.create_invoice(journal_id=self.journal_id)
        # This are particular cases, because this documents doesn't have CDR
        invoice_open_no_cdr.l10n_pe_edi_cdr_date = False
        invoice_open_no_cdr_1.l10n_pe_edi_cdr_date = False

        # This 2 groups are not going to be cancelled
        ticket_open = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        ticket_open_1 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 1))
        ticket_open_no_cdr = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 1))
        ticket_open_no_cdr_1 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 1))
        # This are particular cases, because this documents doesn't have CDR
        ticket_open_no_cdr.l10n_pe_edi_cdr_date = False
        ticket_open_no_cdr_1.l10n_pe_edi_cdr_date = False

        # Cancel all the documents except the _open
        self.cancel_document(
            [invoice_today, invoice_1, invoice_7, invoice_8, invoice_no_cdr,
             invoice_no_cdr_1, invoice_no_cdr_7, invoice_no_cdr_8,
             ticket_today, ticket_1, ticket_7, ticket_8, ticket_no_cdr,
             ticket_no_cdr_1, ticket_no_cdr_7, ticket_no_cdr_8],
            "CANCEL TICKET")

        self.assertEqual(invoice_1.l10n_pe_edi_pse_status, 'to_cancel')
        self.assertEqual(invoice_7.l10n_pe_edi_pse_status, 'to_cancel')

        # This can't be cancelled
        self.message_check([
            invoice_8, invoice_no_cdr_8, ticket_8, ticket_no_cdr_8],
            expected="Create a credit a note", test="assertIn")

        # This documents should not be cancelled and not included in a summary
        self.assertEqual(invoice_8.l10n_pe_edi_pse_status, 'valid',
                         'Document expected to be Valid')
        self.assertEqual(invoice_no_cdr_8.l10n_pe_edi_pse_status, 'signed',
                         'Document expected to be Valid')
        self.assertEqual(ticket_8.l10n_pe_edi_pse_status, 'valid',
                         'Document expected to be Valid')
        self.assertEqual(ticket_no_cdr_8.l10n_pe_edi_pse_status, 'signed',
                         'Document expected to be Valid')

        account_invoice_obj = self.env['account.invoice']
        expected = ("This invoice has been included")

        # Section of days = 0, none shall be included
        account_invoice_obj.l10n_pe_edi_cron_send_voided_documents(days=0)
        self.message_check(
            [invoice_today, invoice_1, invoice_7, invoice_8, invoice_no_cdr,
             invoice_no_cdr_1, invoice_no_cdr_7, invoice_no_cdr_8,
             ticket_today, ticket_1, ticket_7, ticket_8, ticket_no_cdr,
             ticket_no_cdr_1, ticket_no_cdr_7, ticket_no_cdr_8, invoice_open,
             invoice_open_1, invoice_open_no_cdr, invoice_open_no_cdr_1,
             ticket_open, ticket_open_1, ticket_open_no_cdr,
             ticket_open_no_cdr_1], expected=expected, test="assertFalse")

        # Section of days = 8 all documents within 1-7 days will be included
        account_invoice_obj.l10n_pe_edi_cron_send_voided_documents(days=8)
        self.message_check(
            [invoice_today, invoice_8, invoice_no_cdr,
             ticket_8, invoice_no_cdr_8, ticket_today, ticket_no_cdr,
             ticket_no_cdr_8, invoice_open, invoice_open_1,
             invoice_open_no_cdr, invoice_open_no_cdr_1, ticket_open,
             ticket_open_1, ticket_open_no_cdr, ticket_open_no_cdr_1],
            expected=expected, test="assertFalse")

        self.message_check(
            [invoice_1, invoice_7], expected='CDR Received', test="assertIn")

        self.assertEqual(invoice_1.l10n_pe_edi_pse_status, 'in_process')
        self.assertEqual(invoice_7.l10n_pe_edi_pse_status, 'in_process')

        self.account_invoice.l10n_pe_edi_cron_get_status_documents()

        self.assertEqual(invoice_1.l10n_pe_edi_pse_status, 'cancelled')
        self.assertEqual(invoice_7.l10n_pe_edi_pse_status, 'cancelled')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_02_valid_documents_cron_job(self):
        """With this test we are proving the cases that must apply to the cron
        valid documents.
        - The documents can be of the same day
        - The documents can't be from more than 7 days after it's validation
        - Tickets and their related documents are sent in a summary
        - Invoices and their related documents are sent individually
        - Cancelled tickets should not pass the filter of the cron
        """

        invoice_today = self.create_invoice(journal_id=self.journal_id)
        invoice_yesterday_minus_8 = self.create_invoice(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 8))
        ticket_today = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.journal_bol)
        ticket_yesterday_minus_8 = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.journal_bol,
            date=self.date_minus(self.today_date, 8))

        credit_invoice_today = self.create_credit(invoice_today)
        debit_invoice_today = self.create_debit(invoice_today)

        credit_ticket_today = self.create_credit(ticket_today)
        debit_ticket_today = self.create_debit(ticket_today)

        ticket_retry = self.create_invoice(journal_id=self.journal_id)
        ticket_retry.l10n_pe_edi_pse_status = 'retry'

        ticket_cancelled = self.create_invoice(journal_id=self.journal_bol,
                                               partner=self.partner_bol)
        self.cancel_document(ticket_cancelled, "CANCEL TICKET")

        account_invoice_obj = self.env['account.invoice']

        account_invoice_obj.l10n_pe_edi_cron_send_valid_documents()

        lot_expected = ("This invoice has been included")
        individual_expected = ("CDR Received")

        self.message_check(invoice_today, expected=individual_expected)

        self.message_check(ticket_today, expected=lot_expected)

        # No summary or valid to documents that at this point
        self.assertEqual(credit_invoice_today.l10n_pe_edi_pse_status, 'signed')
        self.assertEqual(debit_invoice_today.l10n_pe_edi_pse_status, 'signed')
        self.assertFalse(credit_ticket_today.l10n_pe_edi_summary_id)
        self.assertFalse(debit_ticket_today.l10n_pe_edi_summary_id)

        messages = invoice_yesterday_minus_8.message_ids
        message = messages.filtered(lambda r: individual_expected in r.body)
        self.assertFalse(message)

        self.message_check(ticket_cancelled, expected=lot_expected)
        self.message_check(
            ticket_cancelled,
            expected='This document should run again the summary generation')
        self.message_check(
            [ticket_yesterday_minus_8, ticket_retry],
            expected=lot_expected, test="assertFalse")

    @tools.mute_logger('pysimplesoap.helpers')
    def test_03_get_summary_status(self):
        """Testing all the crons and checking their status code and responses
        Create a ticket, activate the cron summary, cancel the document,
        activate the voided cron and check their status"""
        ticket_yesterday = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 1))
        invoice_1 = self.create_invoice(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 1))

        ticket_yesterday.l10n_pe_edi_cdr_date = False
        invoice_1.l10n_pe_edi_cdr_date = False
        lot_expected = ("This invoice has been included")
        individual_expected = ("CDR Received")

        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice._l10n_pe_edi_prepare_and_send')
        account_invoice = self.env['account.invoice']

        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'signed')
        self.assertEqual(invoice_1.l10n_pe_edi_pse_status, 'signed')
        # Sending this invoice without the cron, because of the mock return
        invoice_1.action_send_to_sunat()

        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_ticket_number_response('1503680600635'))
            account_invoice.l10n_pe_edi_cron_send_valid_documents()
        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'in_process')
        self.message_check(ticket_yesterday, expected=lot_expected,
                           test="assertIn")
        self.message_check(invoice_1, expected=individual_expected,
                           test="assertIn")
        self.assertTrue(invoice_1.l10n_pe_edi_cdr_date,
                        "We expected this document to have a CDR date")
        filename = splitext(
            ticket_yesterday.l10n_pe_edi_summary_id.datas_fname)[0]

        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_custom_statuscode(
                    '0', filename, valid_cdr=True,
                    date=ticket_yesterday.date_invoice))
            account_invoice.l10n_pe_edi_cron_get_status_documents()
        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'valid')
        summary_name = ticket_yesterday.l10n_pe_edi_summary_id.name
        cdr_received = 'A CDR have been received for %s' % summary_name
        self.message_check(ticket_yesterday, cdr_received, 'assertIn')
        self.assertTrue(ticket_yesterday.l10n_pe_edi_cdr_date,
                        "We expected this document to have a CDR date")

        self.message_check(
            ticket_yesterday, expected=lot_expected, test="assertIn")

        self.cancel_document([ticket_yesterday, invoice_1], "CANCEL TICKET")
        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'to_cancel')
        self.assertEqual(invoice_1.l10n_pe_edi_pse_status, 'to_cancel')

        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_ticket_number_response('1503000600835'))
            account_invoice.l10n_pe_edi_cron_send_voided_documents(days=1)
        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'to_cancel')
        self.assertEqual(invoice_1.l10n_pe_edi_pse_status, 'in_process')

        # Changing the name because we know invoice_1 cames as zip name
        filename = splitext(
            invoice_1.l10n_pe_edi_summary_id.datas_fname)[0]
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_custom_statuscode(
                    '0', filename, valid_cdr=True,
                    date=ticket_yesterday.date_invoice))
            account_invoice.l10n_pe_edi_cron_get_status_documents()

        summary_name = invoice_1.l10n_pe_edi_summary_id.name
        cdr_received = 'A CDR have been received for %s' % summary_name
        self.message_check(ticket_yesterday, cdr_received, 'assertFalse')

        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'to_cancel')
        self.assertEqual(invoice_1.l10n_pe_edi_pse_status, 'cancelled')

    def test_04_resend_summary(self):
        """Testing what happend and what should happend if a summary gets an
        error when sending it to SUNAT"""
        ticket_1 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,)
        ticket_1a = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,)
        ticket_2 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 1))
        ticket_2a = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 1))

        ticket_1.l10n_pe_edi_cdr_date = False
        ticket_1a.l10n_pe_edi_cdr_date = False
        ticket_2.l10n_pe_edi_cdr_date = False
        ticket_2a.l10n_pe_edi_cdr_date = False

        lot_expected = ("This invoice has been included")
        fail_expected = ("No se pudo procesar su solicitud.")
        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice._l10n_pe_edi_prepare_and_send')
        account_invoice = self.env['account.invoice']

        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'signed')
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'signed')

        # Mocking a failure when sending the document
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_custom_response('0200'))
            account_invoice.l10n_pe_edi_cron_send_valid_documents()

        self.assertTrue(ticket_1.l10n_pe_edi_summary_id !=
                        ticket_2.l10n_pe_edi_summary_id)
        self.assertTrue(ticket_1.l10n_pe_edi_summary_id ==
                        ticket_1a.l10n_pe_edi_summary_id)
        self.assertTrue(ticket_2.l10n_pe_edi_summary_id ==
                        ticket_2a.l10n_pe_edi_summary_id)
        # Document in process, because wasn't received and has no ticket_number
        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'in_process')
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'in_process')
        self.message_check(
            ticket_1, expected=fail_expected, test="assertIn")
        self.assertFalse(ticket_1.l10n_pe_edi_ticket_number)
        self.message_check(
            ticket_2, expected=fail_expected, test="assertIn")
        self.assertFalse(ticket_2.l10n_pe_edi_ticket_number)

        # Sending it again should generate a ticket_1 number
        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'in_process')
        self.message_check(ticket_1, expected=lot_expected,
                           test="assertIn")
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'in_process')
        self.message_check(ticket_2, expected=lot_expected,
                           test="assertIn")
        # This is just to ckeck if it's not going to mess with new tickets
        ticket_3 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,)
        ticket_3a = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,)
        ticket_4 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 1))
        ticket_4a = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 1))
        ticket_3.l10n_pe_edi_cdr_date = False
        ticket_3a.l10n_pe_edi_cdr_date = False
        ticket_4.l10n_pe_edi_cdr_date = False
        ticket_4a.l10n_pe_edi_cdr_date = False
        # This time the cron should include the sumary that wasn't sent
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_ticket_number_response('1503680600635'))
            account_invoice.l10n_pe_edi_cron_send_valid_documents()

        # With this we ensure the documents aren't merged
        self.assertTrue(ticket_1.l10n_pe_edi_summary_id !=
                        ticket_3.l10n_pe_edi_summary_id)
        self.assertTrue(ticket_1.l10n_pe_edi_summary_id ==
                        ticket_1a.l10n_pe_edi_summary_id)
        self.assertTrue(ticket_3.l10n_pe_edi_summary_id ==
                        ticket_3a.l10n_pe_edi_summary_id)
        self.assertTrue(ticket_4.l10n_pe_edi_summary_id !=
                        ticket_2.l10n_pe_edi_summary_id)
        self.assertTrue(ticket_4.l10n_pe_edi_summary_id ==
                        ticket_4a.l10n_pe_edi_summary_id)

        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'in_process')
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'in_process')
        self.assertEqual(ticket_3.l10n_pe_edi_pse_status, 'in_process')
        self.assertEqual(ticket_4.l10n_pe_edi_pse_status, 'in_process')

        # This method will mock the get status for all
        self.check_status([ticket_1a, ticket_2a, ticket_3a])

        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_1a.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_2a.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_3.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_3a.l10n_pe_edi_pse_status, 'valid')
        # Leaving this 2 out to ensure it's working properly
        self.assertEqual(ticket_4.l10n_pe_edi_pse_status, 'in_process')
        self.assertEqual(ticket_4a.l10n_pe_edi_pse_status, 'in_process')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_05_send_only_valid_invoices(self):
        """Test boletas are not read from SUNAT individually when cron is
        executed
        """
        invoice = self.create_invoice()
        ticket = self.create_invoice(journal_id=self.journal_bol,
                                     partner=self.partner_bol)

        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'signed')
        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'signed')

        self.env['account.invoice'].l10n_pe_edi_cron_send_valid_documents()

        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'valid')
        resp = ('The service you are trying to consume is not responding with'
                ' an xml')
        m_bodies = ticket.mapped('message_ids.body')
        self.assertFalse(any(msg for msg in m_bodies if resp in msg),
                         'Ticket cannot be read individually')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_06_related_and_to_cancel_documents(self):
        """Testing the new cron that sends the tickets(03) and credit/debit
        documents (07,08).
        """
        invoice = self.create_invoice()

        ticket_a = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        ticket_b = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)

        credit = self.create_credit(ticket_b)
        debit = self.create_debit(ticket_b)

        self.account_invoice.l10n_pe_edi_cron_send_valid_documents()
        ticket_c = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        # Proving that 03 are ignores if not cancelled
        self.account_invoice.l10n_pe_edi_cron_send_valid_documents(
            doc_type='second_wave')
        self.assertEquals(invoice.l10n_pe_edi_pse_status, 'valid')
        self.assertEquals(ticket_a.l10n_pe_edi_pse_status, 'in_process')
        self.assertEquals(ticket_b.l10n_pe_edi_pse_status, 'in_process')
        self.assertEquals(ticket_c.l10n_pe_edi_pse_status, 'signed')
        self.assertEquals(credit.l10n_pe_edi_pse_status, 'signed')
        self.assertEquals(debit.l10n_pe_edi_pse_status, 'signed')

        self.cancel_document(ticket_a, "CANCEL A TICKET")
        self.account_invoice.l10n_pe_edi_cron_get_status_documents()

        # Sending the pending documents, the cancelled and related ones
        self.account_invoice.l10n_pe_edi_cron_send_valid_documents(
            doc_type='second_wave')
        self.assertEquals(ticket_a.l10n_pe_edi_pse_status, 'to_be_cancelled')
        self.assertEquals(ticket_b.l10n_pe_edi_pse_status, 'valid')
        self.assertEquals(ticket_c.l10n_pe_edi_pse_status, 'signed')
        self.assertEquals(credit.l10n_pe_edi_pse_status, 'in_process')
        self.assertEquals(debit.l10n_pe_edi_pse_status, 'in_process')

        self.account_invoice.l10n_pe_edi_cron_get_status_documents()
        self.assertEquals(ticket_a.l10n_pe_edi_pse_status, 'to_cancel')
        self.assertEquals(ticket_b.l10n_pe_edi_pse_status, 'valid')
        self.assertEquals(ticket_c.l10n_pe_edi_pse_status, 'signed')
        self.assertEquals(credit.l10n_pe_edi_pse_status, 'valid')
        self.assertEquals(debit.l10n_pe_edi_pse_status, 'valid')

        # This is the main purpose of this cron, send again this documents
        self.account_invoice.l10n_pe_edi_cron_send_valid_documents(
            doc_type='second_wave')
        self.assertEquals(ticket_a.l10n_pe_edi_pse_status, 'in_process')
        self.account_invoice.l10n_pe_edi_cron_get_status_documents()
        self.assertEquals(ticket_a.l10n_pe_edi_pse_status, 'cancelled')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_06_resend_forgotten_summaries(self):
        """Proving that summaries that were having troubles in the last daily
        execution are currently being send with the second_wave cron
        """
        second_date = self.date_minus(self.yesterday_date, 2)
        ticket_wiz_a = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.yesterday_date)
        ticket_wiz_b = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=second_date)

        ticket_wiz_a.l10n_pe_edi_cdr_date = False
        ticket_wiz_b.l10n_pe_edi_cdr_date = False
        wizard = self.create_wizard_summary(self.yesterday_date, 'rc')
        wizard.generate_document()

        wizard = self.create_wizard_summary(second_date, 'rc')
        wizard.generate_document()

        self.assertFalse(ticket_wiz_a.l10n_pe_edi_ticket_number)
        self.assertFalse(ticket_wiz_b.l10n_pe_edi_ticket_number)

        # This cron can send the documents, but testing it with second_wave
        # because this configuration runs several times a day
        self.account_invoice.l10n_pe_edi_cron_send_valid_documents(
            doc_type='second_wave')
        self.assertTrue(ticket_wiz_a.l10n_pe_edi_ticket_number)
        self.assertTrue(ticket_wiz_b.l10n_pe_edi_ticket_number)
        self.assertEquals(ticket_wiz_a.l10n_pe_edi_pse_status, 'in_process')
        self.assertEquals(ticket_wiz_b.l10n_pe_edi_pse_status, 'in_process')
