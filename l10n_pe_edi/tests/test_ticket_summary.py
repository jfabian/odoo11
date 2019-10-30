# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from os.path import splitext

import mock
from lxml.etree import fromstring

from odoo import tools
from odoo.exceptions import UserError

from .test_common import TestCommon


class TestTicketSummary(TestCommon):

    def create_invoices_bol(self):
        invoices = self.env['account.invoice']

        # Create 1st boleta
        invoice = self.create_invoice(partner=self.partner_bol,
                                      journal_id=self.journal_bol)
        invoices += invoice

        # Create 2nd boleta
        invoice = self.create_invoice(partner=self.partner_bol,
                                      journal_id=self.journal_bol)
        invoices += invoice

        # create debit note
        wizard = self.env['account.invoice.refund'].with_context({
            'active_ids': invoice.ids,
        }).create({
            'description': 'Debit note from unit test',
            'filter_refund': 'charge',
            'l10n_pe_charge_reason': '02',
        })
        wizard.invoice_refund()

        # create credit note
        wizard = self.env['account.invoice.refund'].with_context({
            'active_ids': invoice.ids,
        }).create({
            'description': 'Credit note from unit test',
            'filter_refund': 'refund',
            'l10n_pe_refund_reason': '04',
        })
        wizard.invoice_refund()
        notes = self.env['account.invoice'].search(
            [('refund_invoice_id', '=', invoice.id)])
        notes.action_invoice_open()
        invoices += notes
        return invoices

    def test_01_test_ticket_summary(self):
        today = self.env['l10n_pe_edi.certificate'].get_pe_current_datetime()
        date_invoice = today.date().strftime('%Y-%m-%d')
        self.create_invoices_bol()
        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        wizard = wizard_obj.create({'reference_date': date_invoice,
                                    'summary_type': 'rc'})
        attachment_id = wizard.generate_document()
        attachment = self.env['ir.attachment'].browse(attachment_id)
        attachment_name = attachment.datas_fname
        invoices = self.env['account.invoice'].search(
            [('l10n_pe_edi_summary_id', 'in', attachment_id)])
        self.assertEqual(set(invoices.mapped('l10n_pe_edi_pse_status')),
                         set(['in_process']), 'Invoice in a Ticket summary '
                         'must be in process')
        self.assertEqual(len(invoices), 2, 'Only 2 tickets are allowed to be'
                         ' in this first phase, credit/debit notes are left')
        self.assertIn('20565520572', attachment_name)
        self.assertIn('RC', attachment_name)
        self.assertIn('zip', attachment_name)

    @mock.patch('odoo.addons.l10n_pe_edi.models.account_invoice.AccountInvoice'
                '._l10n_pe_edi_prepare_and_send')
    def test_02_cancelled_after_summary_creation(self, mock_get_status):
        """Create 3 documents, create a summary wizard, cancel one of the
        documents and expect that the state of the untouched boletas being
        defined by the SUNAT response leaving 1 cancelled and 2 valid.
        After that the cancelled document must be ready to be included in
        another ticket summary"""

        today = self.env['l10n_pe_edi.certificate'].get_pe_current_datetime()
        today_date = today.date().strftime(
            tools.DEFAULT_SERVER_DATE_FORMAT)
        ticket_1 = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.journal_bol)
        ticket_2 = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.journal_bol)
        ticket_3 = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.journal_bol)
        wizard = self.create_wizard_summary(today_date, 'rc')
        wizard.generate_document()

        # all three docs must be included in the same summary
        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'in_process')
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'in_process')
        self.assertEqual(ticket_3.l10n_pe_edi_pse_status, 'in_process')

        # after cancelling a in_process document it must be ready to be taken
        # in a ticket summary
        self.cancel_document(ticket_3, 'No reason')
        self.assertEqual(ticket_3.l10n_pe_edi_pse_status, 'to_cancel')
        self.assertFalse(ticket_3.l10n_pe_edi_summary_id,
                         'Must be unrelated to a summary')
        self.assertFalse(ticket_3.l10n_pe_edi_ticket_number,
                         'After being cancelled it must be have '
                         'no ticket number')

        filename = splitext(
            ticket_1.l10n_pe_edi_summary_id.datas_fname)[0]

        mock_get_status.return_value = fromstring(
            self.get_custom_statuscode(
                '0', filename, valid_cdr=True,
                date=ticket_1.date_invoice))
        ticket_1.l10n_pe_edi_action_get_status_sunat()
        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_3.l10n_pe_edi_pse_status, 'to_cancel')

        wizard = self.create_wizard_summary(today_date, 'rc')
        wizard.generate_document()
        self.assertEqual(ticket_1.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_2.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_3.l10n_pe_edi_pse_status, 'to_be_cancelled')

    def test_03_test_regenerate_summary(self):
        """Creating a ticket from a fixed date, put it in a summary, the name
        and date should be equal after the summary regenerate"""

        date_str = '2017-01-01'
        ticket_3 = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date=date_str)

        # This is aparticular case, because this document doesn't have CDR
        ticket_3.l10n_pe_edi_cdr_date = False
        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        wizard = wizard_obj.create({'reference_date': date_str,
                                    'summary_type': 'rc'})

        attachment_id = wizard.generate_document()

        summary_name = "%s-RC-%s-1.zip" % (
            ticket_3.company_id.partner_id.l10n_pe_vat_number,
            self.today_date.replace('-', ''))

        self.assertFalse(ticket_3.l10n_pe_edi_ticket_number)
        self.assertEqual(ticket_3.l10n_pe_edi_summary_id.name, summary_name)
        attachment = self.env['ir.attachment'].browse(attachment_id)
        attachment_name = attachment.datas_fname
        invoices = self.env['account.invoice'].search(
            [('l10n_pe_edi_summary_id', 'in', attachment_id)])
        self.assertEqual(set(invoices.mapped('l10n_pe_edi_pse_status')),
                         set(['in_process']), 'Invoice in a Ticket summary '
                         'must be in process')
        self.assertIn('20565520572', attachment_name)
        self.assertIn('RC', attachment_name)
        self.assertIn('zip', attachment_name)

        invoices.l10n_pe_edi_action_regenerate()
        summary_name = "%s-RC-%s-2.zip" % (
            ticket_3.company_id.partner_id.l10n_pe_vat_number,
            self.today_date.replace('-', ''))

        self.assertFalse(ticket_3.l10n_pe_edi_ticket_number)
        self.assertEqual(ticket_3.l10n_pe_edi_summary_id.name, summary_name)
        self.assertEqual(ticket_3.date_invoice, date_str)

        ticket_3.l10n_pe_edi_pse_status = 'with_error'
        invoices.l10n_pe_edi_action_regenerate()
        summary_name = "%s-RC-%s-3.zip" % (
            ticket_3.company_id.partner_id.l10n_pe_vat_number,
            self.today_date.replace('-', ''))

        self.assertEqual(ticket_3.l10n_pe_edi_summary_id.name, summary_name)
        self.assertEqual(ticket_3.date_invoice, date_str)

    def test_04_regenerate_index(self):
        """When regenerating the next index for the summary to be regenerated
        must be according to the sequence no matter the gaps in between
        """

        indexes = ['3', '9', '11', '16', '20', '29', '44']
        name = "20565520572-RC-20170101-%s.zip"
        for tail_index in indexes:
            self.env["ir.attachment"].create({
                'name': name % tail_index,
            })

        attachment = self.env['ir.attachment'].search([
            ('name', '=', name % '29')])
        ticket = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol,
            date='2017-01-01')
        ticket.l10n_pe_edi_summary_id = attachment.id

        ticket.l10n_pe_edi_action_regenerate()
        self.assertEqual('20565520572-RC-20170101-45.zip',
                         ticket.l10n_pe_edi_summary_id.name,
                         'Next index expected would be 45 for RC')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_05_different_summary_generation(self):
        """After some update in the summary generation we need to be sure that
        the generation of summaries is still intact and functional, so we are
        generating summaries manually, with the cron and regenerating. Also,
        we are adding the cancelation of documents inside summaries now.
        """
        # Manually
        ticket_manually = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        wizard = wizard_obj.create({'reference_date': self.today_date,
                                    'summary_type': 'rc'})
        wizard.generate_document()
        ticket_manually.l10n_pe_edi_action_send_summary_sunat()
        self.assertTrue(ticket_manually.l10n_pe_edi_ticket_number,
                        "We expected this document to have a ticket number")
        ticket_manually.l10n_pe_edi_action_get_status_sunat()
        self.assertEqual(ticket_manually.l10n_pe_edi_pse_status, 'valid')

        self.cancel_document(ticket_manually, 'No reason')
        wizard = wizard_obj.create({'reference_date': self.today_date,
                                    'summary_type': 'rc'})
        # Cancel the document to be sure that the manual method will cancel it
        wizard.generate_document()
        ticket_manually.l10n_pe_edi_action_send_summary_sunat()
        ticket_manually.l10n_pe_edi_action_get_status_sunat()
        self.assertEqual(ticket_manually.l10n_pe_edi_pse_status, 'cancelled')

        # With the cron
        ticket_dual = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        self.env['account.invoice'].l10n_pe_edi_cron_send_valid_documents()
        self.assertTrue(ticket_dual.l10n_pe_edi_ticket_number,
                        "We expected this document to have a ticket number")
        ticket_dual.l10n_pe_edi_action_get_status_sunat()
        self.assertEqual(ticket_dual.l10n_pe_edi_pse_status, 'valid')

        self.assertFalse(ticket_dual.l10n_pe_edi_ticket_number)
        self.assertNotEqual(ticket_manually.l10n_pe_edi_summary_id.name,
                            ticket_dual.l10n_pe_edi_summary_id.name)

        # Regenerate one of the above
        ticket_dual.l10n_pe_edi_action_regenerate()
        ticket_dual.l10n_pe_edi_action_send_summary_sunat()
        self.assertTrue(ticket_dual.l10n_pe_edi_ticket_number,
                        "We expected this document to have a ticket number")
        ticket_dual.l10n_pe_edi_action_get_status_sunat()
        self.assertEqual(ticket_dual.l10n_pe_edi_pse_status, 'valid')

        # Cancel the document to be sure that the cron will clean that
        self.cancel_document(ticket_dual, 'No reason')
        self.env['account.invoice'].l10n_pe_edi_cron_send_valid_documents()
        ticket_dual.l10n_pe_edi_action_get_status_sunat()
        self.assertEqual(ticket_dual.l10n_pe_edi_pse_status, 'cancelled')

    @mock.patch('odoo.addons.l10n_pe_edi.models.account_invoice.AccountInvoice'
                '._l10n_pe_edi_prepare_and_send')
    def test_06_text_as_status_code(self, mock_get_status):
        today = self.env['l10n_pe_edi.certificate'].get_pe_current_datetime()
        today_date = today.date().strftime(
            tools.DEFAULT_SERVER_DATE_FORMAT)
        ticket = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.journal_bol)
        wizard = self.create_wizard_summary(today_date, 'rc')
        wizard.generate_document()

        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'in_process')

        filename = splitext(
            ticket.l10n_pe_edi_summary_id.datas_fname)[0]

        mock_get_status.return_value = fromstring(
            self.get_custom_statuscode(
                'SUNAT does not have a reply at the moment, please stand by',
                filename, valid_cdr=True,
                date=ticket.date_invoice))
        ticket.l10n_pe_edi_action_get_status_sunat()
        self.message_check(
            ticket, expected='SUNAT does not have a reply at the moment')
        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'in_process')

    @mock.patch('odoo.addons.l10n_pe_edi.models.account_invoice.AccountInvoice'
                '._l10n_pe_edi_prepare_and_send')
    def test_07_code_98(self, mock_get_status):
        today = self.env['l10n_pe_edi.certificate'].get_pe_current_datetime()
        today_date = today.date().strftime(
            tools.DEFAULT_SERVER_DATE_FORMAT)
        ticket = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.journal_bol)
        wizard = self.create_wizard_summary(today_date, 'rc')
        wizard.generate_document()

        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'in_process')

        filename = splitext(
            ticket.l10n_pe_edi_summary_id.datas_fname)[0]

        mock_get_status.return_value = fromstring(
            self.get_custom_statuscode(
                '98', filename, valid_cdr=True,
                date=ticket.date_invoice))
        ticket.l10n_pe_edi_action_get_status_sunat()
        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'in_process')

    def test_08_twice_summary_not_allowed(self):
        """Testing that generating a summary again from a document in_process
        should not be allowed"""
        ticket = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.journal_bol)
        self.create_wizard_summary(self.today_date, 'rc').generate_document()
        with self.assertRaises(UserError):
            self.create_wizard_summary(
                self.today_date, 'rc').generate_document()

        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'in_process')
