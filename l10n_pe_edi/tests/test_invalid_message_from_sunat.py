# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import mock
from lxml.etree import fromstring

from .test_common import TestCommon


class TestNoResponseMessage(TestCommon):

    @mock.patch('odoo.addons.l10n_pe_edi.models.account_invoice.AccountInvoice'
                '._l10n_pe_edi_prepare_and_send')
    def test_01_xml_creation_for_sunat_response(self, mock_prepare_and_send):
        """Generate an invoice and send to SUNAT provoking an error
        and check document can be sent again"""
        invoice = self.create_invoice()
        response = self.get_custom_response('0103')
        mock_prepare_and_send.return_value = fromstring(response)
        invoice.action_send_to_sunat()
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'signed',
                         'Error code exception received and the document '
                         'needs to ready to be sent again')
        message = self.env['mail.message'].search(
            [('res_id', '=', invoice.id),
             ('subject', '=', u'Error received from SUNAT')], limit=1)
        body = u'El Usuario ingresado no existe'
        self.assertIn(body, message.body, 'A message was expected')

    @mock.patch('odoo.addons.l10n_pe_edi.models.account_invoice.AccountInvoice'
                '._l10n_pe_edi_prepare_and_send')
    def test_02_rejected_doc(self, mock_prepare_and_send):
        """Generate a invoice, provoke an rejection error and check document
        have been rejected by SUNAT and set as well"""
        invoice = self.create_invoice()
        response = self.get_custom_response('0200')
        mock_prepare_and_send.return_value = fromstring(response)
        invoice.action_send_to_sunat()
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'signed',
                         'Error without exception received and the document '
                         'needs to set as rejected')

    @mock.patch('odoo.addons.l10n_pe_edi.models.account_invoice.AccountInvoice'
                '._l10n_pe_edi_prepare_and_send')
    def test_03_get_warning_from_sunat(self, mock_prepare_and_send):
        """Generate a invoice, provoke an warning error and check document
        is valid but having a message in the chatter"""
        invoice = self.create_invoice()
        response = self.get_custom_response('4000', 'WARNING MESSAGE')
        mock_prepare_and_send.return_value = fromstring(response)
        invoice.action_send_to_sunat()
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'valid',
                         'Document must be valid even an error code have been '
                         'received')
        self.assertIn('<p>Code: 4000<br>Message: WARNING MESSAGE</p>',
                      invoice.mapped('message_ids.body'),
                      'Warning message must be posted even the document is '
                      'valid for SUNAT')
