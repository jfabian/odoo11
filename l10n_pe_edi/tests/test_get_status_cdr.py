# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from os.path import splitext

import mock
from lxml.objectify import fromstring

from odoo import tools

from .test_common import TestCommon


class TestGetStatusCdr(TestCommon):

    @tools.mute_logger('pysimplesoap.helpers')
    def test_01_get_cdr_status(self):
        """Testing the get_status_cdr method to retrieve an invoice cdr
        response from the sunat"""
        invoice = self.create_invoice(journal_id=self.journal_id)
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'signed')

        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice._l10n_pe_edi_prepare_and_send')

        filename = splitext(invoice.l10n_pe_edi_ublpe_name)[0]
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_custom_getstatuscdr(filename=filename))
            invoice.l10n_pe_edi_action_get_status_cdr_sunat()

        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(invoice.l10n_pe_edi_cdr_date, '2017-01-01')
        self.assertIn('A CDR have been recovered for %s.zip' % filename,
                      invoice.message_ids[0].body, 'Expected message for CDR '
                      'recovered with getStatusCdr')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_02_no_content_in_getStatusCdr(self):
        """Testing the process of not getting content from the SUNAT in the XML
        but still getting a passed document because of the good code response
        from the sunat"""
        invoice = self.create_invoice(journal_id=self.journal_id)
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'signed')

        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice._l10n_pe_edi_prepare_and_send')

        filename = splitext(invoice.l10n_pe_edi_ublpe_name)[0]
        tree = fromstring(self.get_custom_getstatuscdr(
            filename=filename, content=False))
        bad = tree.xpath("//content")[0]
        bad.getparent().remove(bad)

        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = tree
            invoice.l10n_pe_edi_action_get_status_cdr_sunat()
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'valid')
        self.message_check(
            invoice, 'There is no //content label in the response')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_03_no_content_in_getStatusCdr_invalid_document(self):
        """Testing the process of getting no content from SUNAT and in the XML
        a faulty code meaning that the document is with_error"""
        invoice = self.create_invoice(journal_id=self.journal_id)
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'signed')

        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice._l10n_pe_edi_prepare_and_send')

        filename = splitext(invoice.l10n_pe_edi_ublpe_name)[0]
        # Faulty code 0002
        tree = fromstring(self.get_custom_getstatuscdr(
            filename=filename, content=False, code='0002'))
        bad = tree.xpath("//content")[0]
        bad.getparent().remove(bad)

        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = tree
            invoice.l10n_pe_edi_action_get_status_cdr_sunat()
        self.message_check(
            invoice, 'There is no //content label in the response')
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'with_error')
