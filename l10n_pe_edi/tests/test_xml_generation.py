# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from datetime import datetime

import pytz

from odoo import tools
from odoo.exceptions import UserError

from .test_common import TestCommon


class TestXmlGeneration(TestCommon):

    def setUp(self):
        super(TestXmlGeneration, self).setUp()
        self.tax_id = self.env['account.tax'].search(
            [('name', '=', 'IGV 18% Venta'), ('amount', '=', 18.0)])
        self.invoice = self.create_invoice(journal_id=self.journal_id,
                                           tax_ids=self.tax_id.ids)

    def test_01_pse_version(self):
        self.assertEqual(self.invoice.l10n_pe_edi_get_pse_version(), '2.0',
                         'Current version stands on 2.0, a different is '
                         'being returned')

    def test_02_xml_name_set(self):
        self.assertTrue(self.invoice.l10n_pe_edi_ublpe_name,
                        'Xml file name was not set when generating the xml')
        attachment = self.invoice.l10n_pe_edi_retrieve_last_attachment()
        self.assertEqual(attachment.datas_fname,
                         self.invoice.l10n_pe_edi_ublpe_name,
                         "Attachment file have been generated, please check "
                         "chatter for more info")

    @tools.mute_logger('pysimplesoap.helpers')
    def test_03_ready_to_cancel_invoice(self):
        """After validate an invoice to SUNAT, it gets ready to be notify
        to SUNAT to be cancelled"""
        self.assertEqual(self.invoice.l10n_pe_edi_pse_status, 'signed',
                         "Document isn't signed yet, please check the chatter "
                         "for related errors")

        self.invoice.action_send_to_sunat()

        self.assertEqual(self.invoice.l10n_pe_edi_pse_status, 'valid',
                         'Invoice requires to be valid in SUNAT before '
                         'be cancelled')
        self.cancel_document(self.invoice, u"CANCELADO POR EXTRAVÍO")
        self.assertEqual(self.invoice.l10n_pe_edi_pse_status, 'to_cancel',
                         'Status was expected to be ready to be cancel later '
                         'by another process')

    def test_04_check_invoice_date_localized(self):
        xmldoc = self.invoice.l10n_pe_edi_get_xml_etree()
        invoice_date_tz = self.invoice.l10n_pe_edi_xpath(xmldoc,
                                                         './cbc:IssueDate')[0]
        current_date_tz = datetime.now(pytz.timezone('America/Lima'))
        current_date_tz = current_date_tz.strftime("%Y-%m-%d")
        self.assertEqual(invoice_date_tz, current_date_tz, "Invoice date "
                         "does not matches with America/Lima timezoned one")

    def test_05_ticket_not_vat_amount_le700(self):
        """Create a Boleta with an amount equal to 700 for a customer with no
        VAT set and validate the generic DNI into the XML file
        """
        partner = self.env.ref('base.res_partner_18')
        invoice = self.create_invoice(
            partner=partner, journal_id=self.journal_bol)
        xmldoc = invoice.l10n_pe_edi_get_xml_etree()
        customer_dni = invoice.l10n_pe_edi_xpath(
            xmldoc, './cac:AccountingCustomerParty/'
            'cbc:CustomerAssignedAccountID')[0].text
        self.assertEqual(customer_dni, '00000000',
                         'Generic DNI was expected to be set due the customer '
                         'doesnt have one and the invoice is less than S/ 700')

    def test_06_ticket_not_vat_amount_gt700(self):
        """Create a Boleta with an amount >700 for a customer with no VAT set
        and validate a message gets raised
        """
        partner = self.env.ref('base.res_partner_18')
        with self.assertRaisesRegexp(
            UserError, 'VAT cannot be empty, is required the customer contains'
                ' a valid VAT for the following cases.*'):
            self.create_invoice(partner=partner, journal_id=self.journal_bol,
                                invoice_amount=701)

    def test_07_invoice_not_vat_set(self):
        """Create a invoice for a customer with no VAT set and validate a
        message gets raised
        """
        partner = self.env.ref('base.res_partner_18')
        with self.assertRaisesRegexp(
            UserError, 'VAT cannot be empty, is required the customer contains'
                ' a valid VAT for the following cases.*'):
            self.create_invoice(partner=partner, invoice_amount=50)

    @tools.mute_logger('pysimplesoap.helpers')
    def test_08_signed_to_cancel(self):
        """Invoices of type 01-Factura after being signed (normal validation
        process) must be signed and sent to SUNAT before being cancelled,
        if this is the case and it have not been sent still by the user/cron
        the logic should automatically send and then set ready to be notified
        in a voided communication"""
        self.assertEqual(self.invoice.state, 'open', 'Invoice must be opened')
        self.assertEqual(self.invoice.l10n_pe_edi_pse_status, 'signed',
                         'Invoice must be signed')
        self.invoice.action_invoice_cancel()
        self.assertEqual(self.invoice.state, 'cancel',
                         'Expected to be cancelled')
        self.assertEqual(self.invoice.l10n_pe_edi_pse_status, 'to_cancel',
                         'Expected to be To cancel')
