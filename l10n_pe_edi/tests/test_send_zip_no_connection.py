# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import mock
import pysimplesoap

from odoo import _, tools

from .test_common import NoConnectionMock, TestCommon


class TestNoConection(TestCommon):

    @tools.mute_logger('pysimplesoap.helpers',
                       'odoo.addons.l10n_pe_edi.models.account_invoice')
    def test_01_xml_creation_for_ivoice(self):
        """Generate a invoice, and validate error generated
        when a error connection is raised."""

        invoice = self.create_invoice()
        with mock.patch.object(pysimplesoap.client.SoapClient,
                               '__init__', new=NoConnectionMock):
            invoice.action_send_to_sunat()

        message = self.env['mail.message'].search(
            [('res_id', '=', invoice.id),
             ('subject', '=', _('Error connecting to server'))], limit=1)
        body = _('Please try again later')
        self.assertIn(body, message.body,
                      'An connection error was expected')

    @tools.mute_logger('pysimplesoap.helpers',
                       'odoo.addons.l10n_pe_edi.models.account_invoice')
    def test_02_get_bad_cdr_status(self):
        """Getting an invalid CDR should stop the cancelling process"""
        invoice = self.create_invoice(journal_id=self.journal_id)
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'signed')

        with mock.patch.object(pysimplesoap.client.SoapClient,
                               '__init__', new=NoConnectionMock):
            invoice.action_invoice_cancel()
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'signed')
        self.assertEqual(invoice.state, 'open')
        self.assertEqual(invoice.l10n_pe_edi_cdr_date, False)
