# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from os.path import splitext
from xml.parsers.expat import ExpatError

from lxml.etree import fromstring
import mock
from mock import patch
import pysimplesoap

from odoo import tools
from odoo.exceptions import UserError

from .test_common import TestCommon


class SideEffectAtributeError(object):

    def __init__(self, **kwargs):
        raise AttributeError


class SideEffectExpatError(object):

    def __init__(self, **kwargs):
        raise ExpatError


class TestCatchAllErrors(TestCommon):

    @tools.mute_logger('pysimplesoap.helpers')
    def test_01_catch_AtributeError(self):
        """Send an invoice to the SUNAT while mocking a AttributeError
           this error is raised just after the service has been called.
        """
        invoice = self.create_invoice()
        with patch.object(pysimplesoap.client.SoapClient, '__init__',
                          new=SideEffectAtributeError):
            invoice.action_send_to_sunat()

        error_message = invoice.message_ids.filtered(
            lambda r: 'We got a problem while processing' in r.body)
        expected_message = 'General error cached'
        self.assertEqual(error_message.subject, expected_message)

    @tools.mute_logger('pysimplesoap.helpers')
    def test_02_catch_ExpatError(self):
        """Send an invoice to the SUNAT while mocking a ExpathError thrown by
        the service call.
        """
        invoice = self.create_invoice()
        with patch.object(pysimplesoap.client.SoapClient, '__init__',
                          new=SideEffectExpatError):
            invoice.action_send_to_sunat()

        error_message = invoice.message_ids.filtered(
            lambda r: 'We got a problem while processing' in r.body)
        expected_message = 'General error cached'
        self.assertEqual(error_message.subject, expected_message)

    @tools.mute_logger('pysimplesoap.helpers')
    def test_03_catch_no_xml_response(self):
        """Covering the case where sunat sends everything right except the xml
        response
        """
        invoice = self.create_invoice()
        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice.l10n_pe_edi_sunat_send_bill')
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = "Random text"
            invoice.action_send_to_sunat()

        error_message = invoice.message_ids.filtered(
            lambda r: 'The service you are trying to consume' in r.body)
        expected_message = 'No XML as response'
        self.assertEqual(error_message.subject, expected_message)

    @tools.mute_logger('pysimplesoap.helpers')
    def test_04_no_generated_summary(self):
        """We need to be sure that the voided summary isn't working for tickets
        response
        """
        ticket = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        self.account_invoice.l10n_pe_edi_cron_send_voided_documents(days=1)
        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'signed')
        self.assertFalse(ticket.l10n_pe_edi_cdr_date,
                         "This document shouldn't have a CDR date")

        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        wizard = wizard_obj.create({'reference_date': self.today_date,
                                    'summary_type': 'ra'})
        with self.assertRaises(UserError):
            wizard.generate_document()

        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'signed')
        self.assertFalse(ticket.l10n_pe_edi_cdr_date,
                         "This document shouldn't have a CDR date")

    @tools.mute_logger('pysimplesoap.helpers')
    def test_05_negative_summary(self):
        """SUNAT doesn't allow negative values in totals or values, so if we
        got a negative value from the totals or the taxes we should exclude
        that document.
        """
        ticket_positive = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        ticket_negative = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)

        ticket_negative.write({'amount_total': -38.0,
                               'l10n_pe_edi_amount_taxable': -5.8})
        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        wizard = wizard_obj.create({'reference_date': self.today_date,
                                    'summary_type': 'rc'})
        wizard.generate_document()
        self.assertEqual(ticket_positive.l10n_pe_edi_pse_status, 'in_process')
        self.assertEqual(ticket_negative.l10n_pe_edi_pse_status, 'signed')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_06_no_reset_ticket(self):
        """We shouldn't erase the ticket number if the l10n_pe_edi_pse_status
        is not valid or cancelled.
        """
        ticket_a = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        ticket_b = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice._l10n_pe_edi_prepare_and_send')
        self.env['account.invoice'].l10n_pe_edi_cron_send_valid_documents()
        filename = splitext(
            ticket_a.l10n_pe_edi_summary_id.datas_fname)[0]
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_custom_statuscode(
                    '200', filename, valid_cdr=True,
                    date=ticket_a.date_invoice))
            self.account_invoice.l10n_pe_edi_cron_get_status_documents()
        self.assertEqual(ticket_a.l10n_pe_edi_cdr_date, False)
        self.assertEqual(ticket_a.l10n_pe_edi_pse_status, 'with_error')
        self.assertTrue(ticket_a.l10n_pe_edi_ticket_number)
        self.assertEqual(ticket_b.l10n_pe_edi_cdr_date, False)
        self.assertEqual(ticket_b.l10n_pe_edi_pse_status, 'with_error')
        self.assertTrue(ticket_b.l10n_pe_edi_ticket_number)

    @tools.mute_logger('pysimplesoap.helpers')
    def test_07_code_2987(self):
        """Proving that we processing ResponseCode 2987 from a CDR"""
        ticket = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)

        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'signed')

        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice._l10n_pe_edi_prepare_and_send')

        wizard = self.create_wizard_summary(self.today_date, 'rc')
        wizard.generate_document()
        self.account_invoice.l10n_pe_edi_cron_send_valid_documents(
            doc_type='second_wave')

        filename = "%s-RC-%s-1" % (
            ticket.company_id.vat[3:],
            self.today_date.replace('-', ''))
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(self.get_custom_statuscode(
                '2987', filename, valid_cdr=True,
                date=ticket.date_invoice))
            ticket.l10n_pe_edi_action_get_status_sunat()

        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'with_error')
