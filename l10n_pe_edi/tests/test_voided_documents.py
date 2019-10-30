# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import mock
from lxml.objectify import fromstring
from psycopg2 import IntegrityError

from odoo import tools

from .test_common import TestCommon


class TestVoidedDocuments(TestCommon):

    @tools.mute_logger('pysimplesoap.helpers')
    def test_01_test_cancel_one_document(self):
        today = self.env['l10n_pe_edi.certificate'].get_pe_current_datetime()
        date_invoice = today.date().strftime('%Y-%m-%d')
        invoice = self.create_and_send(journal_id=self.journal_id,
                                       date=date_invoice)
        self.assertEqual(invoice.state, 'open', "Invoice MUST be in 'open' "
                         "state before continuing")
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'valid',
                         'Document expected to be Valid status')
        self.cancel_document(invoice, u"CANCELADO POR EXTRAVÍO")
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'to_cancel',
                         'Document expected to be To Cancel status')

        # When cancelled, document should be not attached to summaries
        self.assertFalse(invoice.l10n_pe_edi_summary_id,
                         'Summary must be cleaned')
        self.assertFalse(invoice.l10n_pe_edi_ticket_number,
                         'Ticket Number must be cleaned')
        wizard = self.env['l10n_pe_edi.summary.wizard'].create({
            'reference_date': date_invoice,
            'summary_type': 'ra'})
        attachment_ids = wizard.generate_document()
        attachment = self.env['ir.attachment'].browse(attachment_ids)
        attachment_name = attachment.datas_fname
        invoices = self.env['account.invoice'].search(
            [('l10n_pe_edi_summary_id', 'in', attachment_ids)])
        self.assertEqual(set(invoices.mapped('l10n_pe_edi_pse_status')),
                         set(['in_process']), 'Invoices in a Voided Document '
                         'notification must be in process')
        self.assertIn('20565520572', attachment_name)
        self.assertIn('RA', attachment_name)
        self.assertIn('zip', attachment_name)
        invoice.l10n_pe_edi_action_send_summary_sunat()
        self.assertTrue(invoice.l10n_pe_edi_ticket_number,
                        'A Ticket number must be obtained after the document '
                        'have been sent to SUNAT')
        invoice.l10n_pe_edi_action_get_status_sunat()
        message = 'A CDR have been received for 20565520572-RA-%s' % (
            self.today_date.replace('-', ''))
        self.message_check(invoice, message)

    def test_02_cancel_draft_document(self):
        product = self.env.ref('product.product_product_5')
        invoice = self.env['account.invoice'].with_env(
            self.env(user=self.uid)).create({
                'partner_id': self.env.ref('base.res_partner_2').id,
                'type': 'out_invoice',
                'journal_id': self.journal_id.id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': product.id,
                        'uom_id': product.uom_id.id,
                        'quantity': 1,
                        'price_unit': 600,
                        'name': 'new line #1',
                        'account_id': self.env.ref('l10n_pe.70111_01').id,
                    })
                ],
            })
        invoice.action_invoice_cancel()
        self.assertEqual(invoice.state, 'cancel',
                         'Document expected to be cancel')

    @tools.mute_logger('pysimplesoap.helpers',
                       'odoo.addons.l10n_pe_edi.models.account_invoice')
    def test_03_local_error_when_getting_status(self):
        """Generate a invoice, cancel it and then the document should be
        cancelled locally and don't have been received a cdr"""

        invoice = self.create_invoice(journal_id=self.journal_id)
        self.cancel_document(invoice, "CANCELADO")

        # Its expected an error, this document should not touch SUNAT servers
        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        today = self.env['l10n_pe_edi.certificate'].get_pe_current_datetime()
        date_invoice = today.date().strftime('%Y-%m-%d')
        wizard_obj.create({'reference_date': date_invoice,
                           'summary_type': 'ra'}).generate_document()
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'in_process')

    def test_04_test_cancel_constraint(self):
        invoice = self.create_invoice(journal_id=self.journal_id)
        with self.assertRaises(IntegrityError):
            wizard = self.env['invoice.cancel.wizard'].with_context({
                'active_id': invoice.id}).create({})
            wizard.l10n_pe_cancel_reason = '     ª!"·$%&/)==?¿"|@#½¬[]}:?    '
            wizard.button_cancel_reason()

    def test_05_cancel_after_7_days(self):
        invoice_8 = self.create_and_send(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 8))
        wizard = self.env['invoice.cancel.wizard'].with_context({
            'active_id': invoice_8.id}).create(
                {'l10n_pe_cancel_reason': 'Normal cancel reason'})
        wizard.button_cancel_reason()
        self.message_check(invoice_8, expected="Create a credit a note",
                           test="assertIn")
        self.assertEqual(invoice_8.l10n_pe_edi_pse_status, 'valid',
                         'Document expected to be Valid')

    def test_06_draft_after_valid_cancelled(self):

        ticket_yesterday = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=self.date_minus(self.today_date, 1))
        ticket_yesterday.l10n_pe_edi_cdr_date = False

        account_invoice = self.env['account.invoice']
        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice._l10n_pe_edi_prepare_and_send')

        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'signed')
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_ticket_number_response('1503680600635'))
            account_invoice.l10n_pe_edi_cron_send_valid_documents()

        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'in_process')

        filename = "%s-RC-%s-1" % (
            ticket_yesterday.company_id.vat[3:],
            self.today_date.replace('-', ''))
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_custom_statuscode(
                    '0', filename,
                    date=ticket_yesterday.date_invoice))
            ticket_yesterday.l10n_pe_edi_action_get_status_sunat()
        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'valid')

        ticket_yesterday.action_invoice_draft()
        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'valid')

        self.cancel_document(ticket_yesterday, "CANCEL TICKET")
        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'to_cancel')

        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_ticket_number_response('1503015600835'))
            account_invoice.l10n_pe_edi_cron_send_voided_documents(days=1)
        self.assertEqual(ticket_yesterday.l10n_pe_edi_pse_status, 'to_cancel')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_07_cancel_the_day_7(self):
        """A document in it's seventh day cancelled after the voided cron has
        already departed"""
        invoice_7 = self.create_invoice(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 7))

        cron_current_date = self.env.ref(
            'l10n_pe_edi.ir_cron_send_voided_documents').nextcall
        self.cancel_document(invoice_7, 'The client refused to pay')

        cron_after_cancelled = self.env.ref(
            'l10n_pe_edi.ir_cron_send_voided_documents').nextcall

        self.assertFalse(cron_current_date == cron_after_cancelled)

    def test_08_test_cancel_constraint_3_characters(self):
        ticket = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        wizard = self.env['invoice.cancel.wizard'].with_context({
            'active_id': ticket.id}).create({
                'l10n_pe_cancel_reason': '12'})
        wizard._compute_l10n_pe_cancel_reason_strip()
        self.assertEqual(wizard.l10n_pe_cancel_reason, '')
        self.assertEqual(wizard.l10n_pe_cancel_reason_strip, False)

    @tools.mute_logger('pysimplesoap.helpers')
    def test_09_cancel_after_7_days_with_error(self):
        """Cancelling a document after the 7 without special group shouldn't
        allow us to cancel it but with it."""
        # Without the permission
        invoice_8 = self.create_invoice(
            journal_id=self.journal_id,
            date=self.date_minus(self.today_date, 8))
        self.cancel_document(invoice_8, 'The client refused to pay')

        self.assertEqual(invoice_8.l10n_pe_edi_pse_status, 'signed')
        self.message_check(invoice_8, expected="Create a credit a note",
                           test="assertNotIn")
        self.assertEqual(invoice_8.state, 'open',
                         'Document state should be open')

        # With the permission
        self.env.user.write({'groups_id': [
            (4, self.ref('l10n_pe_edi.res_group_super_user_manager'))]})
        self.cancel_document(invoice_8, 'The client refused to pay, again')
        self.assertEqual(invoice_8.l10n_pe_edi_pse_status, 'to_cancel',
                         'Document state should be to cancel')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_10_ConditionCode_4(self):
        """Tickets that hasn't been informed to SUNAT need to be send as valid
        first before been send as code 3.
        """
        ticket_1 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        ticket_2 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        wizard = wizard_obj.create({'reference_date': self.today_date,
                                    'summary_type': 'rc'})

        self.cancel_document(ticket_2, 'No reason')
        wizard.generate_document()
        ticket_1.l10n_pe_edi_action_send_summary_sunat()
        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'in_process')
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'to_be_cancelled')

        cdr_content = ticket_2.l10n_pe_edi_summary_id
        cdr = ticket_2.l10n_pe_edi_get_xml_etree(
            ublpe=cdr_content.datas, file_name=cdr_content.name)
        self.assertEqual(self.account_invoice.l10n_pe_edi_xpath(
            cdr, '//cac:Status/cbc:ConditionCode')[0], 1)

        ticket_1.l10n_pe_edi_action_get_status_sunat()
        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'to_cancel')
        self.assertEqual(ticket_2.l10n_pe_edi_ticket_number, False)

        wizard = wizard_obj.create({'reference_date': self.today_date,
                                    'summary_type': 'rc'})

        wizard.generate_document()
        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'valid')
        ticket_2.l10n_pe_edi_action_send_summary_sunat()
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'in_process')
        ticket_2.l10n_pe_edi_action_get_status_sunat()

        cdr_content = ticket_2.l10n_pe_edi_summary_id
        cdr = ticket_2.l10n_pe_edi_get_xml_etree(
            ublpe=cdr_content.datas, file_name=cdr_content.name)
        self.assertEqual(self.account_invoice.l10n_pe_edi_xpath(
            cdr, '//cac:Status/cbc:ConditionCode')[0], 3)
        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'cancelled')
