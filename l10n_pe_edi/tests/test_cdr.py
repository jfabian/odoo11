# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import mock
from lxml.etree import fromstring

from odoo import tools

from .test_common import TestCommon


class TestCDR(TestCommon):

    def setUp(self):
        super(TestCDR, self).setUp()
        self.account_receivable = self.env['account.account'].create({
            'code': 'XXXX1',
            'name': 'Sale - Test Payable Account',
            'user_type_id':
            self.env.ref('account.data_account_type_receivable').id,
            'reconcile': True
        })
        self.account_revenue = self.env['account.account'].search([
            ('user_type_id', '=', self.env.ref(
                'account.data_account_type_revenue').id)], limit=1)
        self.product1 = self.env.ref('product.product_product_1')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_01_sunat_cdr_received(self):
        """Send to SUNAT ZIP File and check CDR response"""

        customer = self.env.ref('base.res_partner_1')
        customer.write({
            'vat': u'PER20132377783',
            'country_id': self.env.ref('base.pe').id,
        })
        invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'type': 'out_invoice',
            'invoice_line_ids': [
                (0, 0, {
                    'name': self.product1.name,
                    'product_id': self.product1.id,
                    'quantity': 50,
                    'uom_id': self.product1.uom_id.id,
                    'price_unit': 1.0,
                    'account_id': self.account_revenue.id,
                }),
            ],
            'account_id': self.account_receivable.id,
        })
        invoice.action_invoice_open()
        invoice.action_send_to_sunat()
        # Check attachments: Zip file, CDR Zip file
        zip_name = '%%%(name)s' % ({'name': invoice.l10n_pe_edi_ublpe_name})
        attachments = self.env['ir.attachment'].search(
            [('res_model', '=', 'account.invoice'),
             ('res_id', '=', invoice.id), ('name', 'ilike', zip_name)])
        cdr = any(['CDR' in attachment.name
                   for attachment in attachments])
        self.assertTrue(cdr, "SUNAT's signed zip file response expected")
        self.assertEqual(2, len(attachments),
                         'Expected two zip files attached')

    @tools.mute_logger('pysimplesoap.helpers')
    def test_02_error_code_2027_fixed(self):
        """Validate that a multi-line invoice line description
           does not affects to the invoice xml.
            - Expecting break lines gets replaced when rendering the XML file
            - And after be sent to SUNAT, get approved.
        """
        invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'account_id': self.account_receivable.id,
            'journal_id': self.journal_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': """This
                    is
                    a multi line
                    description""",
                    'product_id': self.product1.id,
                    'quantity': 1,
                    'uom_id': self.product1.uom_id.id,
                    'price_unit': 1.0,
                    'account_id': self.account_revenue.id,
                }),
            ],
        })
        invoice.action_invoice_open()
        xmldoc = invoice.l10n_pe_edi_get_xml_etree()
        description = invoice.l10n_pe_edi_xpath(
            xmldoc, './cac:InvoiceLine/cac:Item/cbc:Description')[0]
        self.assertEqual(description, 'This                     is            '
                         '         a multi line                     '
                         'description')
        invoice.action_send_to_sunat()
        self.assertEqual(invoice.l10n_pe_edi_pse_status, 'valid',
                         "Invoice was rejected by SUNAT")

    @tools.mute_logger('pysimplesoap.helpers')
    def test_03_check_corrupted_cdr(self):
        """Check when a corrupted file is received is ignored and the document
        remain in state 'In process' for later retrieval"""

        # Create a document boleta to be include later in a daily summary
        ticket = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        ticket.l10n_pe_edi_cdr_date = False
        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice._l10n_pe_edi_prepare_and_send')
        filename = "%s-%s-%s" % (
            ticket.company_id.vat[3:],
            ticket.l10n_pe_document_type, ticket.move_name)

        # Receive a ticket number
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_ticket_number_response('1503680600635'))
            self.env['account.invoice'].l10n_pe_edi_cron_send_valid_documents()
        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'in_process')

        # Request status and received okay (code=0) and invalid cdr
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_custom_statuscode(
                    '0', filename, valid_cdr=False,
                    date=ticket.date_invoice))
            self.account_invoice.l10n_pe_edi_cron_get_status_documents()

        # Check doc status, and chatter message indicating corrupted file
        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'with_error')
        self.message_check(ticket, 'SUNAT returned a corrupted CDR file')
        self.assertTrue(ticket.l10n_pe_edi_ticket_number)

    @tools.mute_logger('pysimplesoap.helpers')
    def test_04_negative_document(self):
        customer = self.env.ref('base.res_partner_1')
        customer.write({
            'vat': u'PER20132377783',
            'country_id': self.env.ref('base.pe').id,
        })
        invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'type': 'out_invoice',
            'invoice_line_ids': [
                (0, 0, {
                    'name': self.product1.name,
                    'product_id': self.product1.id,
                    'quantity': 1,
                    'uom_id': self.product1.uom_id.id,
                    'price_unit': -50.0,
                    'account_id': self.account_revenue.id,
                }),
            ],
            'account_id': self.account_receivable.id,
        })
        invoice.action_invoice_open()
        self.assertEqual(invoice.state, 'draft')
        self.assertFalse(invoice.l10n_pe_edi_pse_status)
        self.assertFalse(invoice.number)
        self.message_check(invoice,
                           "SUNAT does not support negative as totals")

    @tools.mute_logger('pysimplesoap.helpers')
    def test_05_zero_amount_free(self):
        """No document with l10n_pe_edi_amount_free = 0 and amount_total = 0
        should be processed as valid"""
        customer = self.env.ref('base.res_partner_1')
        customer.write({
            'vat': u'PER20132377783',
            'country_id': self.env.ref('base.pe').id,
        })
        self.product1.list_price = 0
        invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'type': 'out_invoice',
            'invoice_line_ids': [
                (0, 0, {
                    'name': self.product1.name,
                    'product_id': self.product1.id,
                    'quantity': 1,
                    'uom_id': self.product1.uom_id.id,
                    'price_unit': 0.0,
                    'account_id': self.account_revenue.id,
                }),
            ],
            'account_id': self.account_receivable.id,
        })
        invoice.action_invoice_open()
        self.assertEqual(invoice.state, 'draft')
        self.assertFalse(invoice.l10n_pe_edi_pse_status)
        self.assertFalse(invoice.number)
        self.message_check(
            invoice, "SUNAT does not support 0.0 as sum of all price_units")

    @tools.mute_logger('pysimplesoap.helpers')
    def test_05_0127_code_error(self):
        """Check if the 0127 error is being processed, it's a recursive error
        in production"""

        # Create a document boleta to be include later in a daily summary
        ticket = self.create_invoice(
            journal_id=self.journal_bol, partner=self.partner_bol)
        ticket.l10n_pe_edi_cdr_date = False
        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice._l10n_pe_edi_prepare_and_send')
        filename = "%s-%s-%s" % (
            ticket.company_id.vat[3:],
            ticket.l10n_pe_document_type, ticket.move_name)

        # Receive a ticket number
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_ticket_number_response('1503680600635'))
            self.env['account.invoice'].l10n_pe_edi_cron_send_valid_documents()
        self.assertEqual(ticket.l10n_pe_edi_pse_status, 'in_process')

        # Request status and received okay (code=0) and invalid cdr
        with mock.patch(method_path) as mock_patch:
            mock_patch.return_value = fromstring(
                self.get_custom_statuscode(
                    '0127', filename, valid_cdr=False, encoded=False,
                    date=ticket.date_invoice, content="El ticket no existe"))
            self.account_invoice.l10n_pe_edi_cron_get_status_documents()

        # Check doc status, and chatter message indicating corrupted file
        self.message_check(
            ticket, "SUNAT is sending us this message:")
        self.message_check(
            ticket, "El ticket no existe")
