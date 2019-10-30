# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import base64
import os
import tempfile
import zipfile
from datetime import datetime, timedelta

from lxml import html
from lxml.etree import tostring
from lxml.objectify import fromstring
import mock
from httplib2 import ServerNotFoundError

from odoo import tools
from odoo.tests import common
from odoo.tools import osutil


class NoConnectionMock(object):

    def __init__(self, **kwargs):
        raise ServerNotFoundError


class TestCommon(common.TransactionCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.journal_id = self.env.ref('l10n_pe_edi.journal_efac')
        self.journal_bol = self.env.ref('l10n_pe_edi.journal_ebol')
        self.uid = self.env['res.users'].with_context(
            {'no_reset_password': True}
        ).create({
            'name': 'User billing pe',
            'login': 'pe_billing_user',
            'email': 'pe_billing_user@demo.com',
            'company_id': self.env.ref('base.main_company').id,
            'groups_id': [(6, 0, [self.ref('account.group_account_invoice')])]
        })
        self.partner_bol = self.env.ref('base.res_partner_12')
        today = self.env['l10n_pe_edi.certificate'].get_pe_current_datetime()
        yesterday = today - timedelta(days=1)
        self.yesterday_date = yesterday.date().strftime(
            tools.DEFAULT_SERVER_DATE_FORMAT)
        self.today_date = today.date().strftime(
            tools.DEFAULT_SERVER_DATE_FORMAT)
        self.account_invoice = self.env['account.invoice']

    def create_invoice(self, invoice_amount=700, journal_id=False,
                       tax_ids=False, partner=None, date=None):
        if partner is None:
            partner = self.env.ref('base.res_partner_2')
        product = self.env.ref('product.product_product_5')

        invoice = self.env['account.invoice'].with_env(
            self.env(user=self.uid)).create({
                'partner_id': partner.id,
                'type': 'out_invoice',
                'journal_id': (journal_id or self.journal_id).id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': product.id,
                        'uom_id': product.uom_id.id,
                        'quantity': 1,
                        'price_unit': invoice_amount,
                        'name': 'new line #1',
                        'account_id': self.env.ref('l10n_pe.70111_01').id,
                        'invoice_line_tax_ids': tax_ids and [(6, 0, tax_ids)],
                    })
                ],
            })
        invoice.action_invoice_open()
        if date:
            invoice.update({
                'date_invoice': date,
                'l10n_pe_edi_cdr_date': date
            })
        return invoice

    def create_partner(self, vat=False):
        return self.env['res.partner'].create({
            'name': 'New Partner',
            'vat': vat,
        })

    def create_journal(self, name="Factura", code="FAC"):
        return self.env['account.journal'].create({
            'company_id': self.env.ref('base.main_company').id,
            'name': name,
            'code': code,
            'type': 'sale',
            'update_posted': True
        })

    def get_text(self, report, xpath_str):
        return [el.text.strip() for el in report.xpath(xpath_str)][0]

    def get_report_content(self, doc_id, report_name, lang=False):
        """It returns the content of whole report in HTML to later checks
        """
        return html.document_fromstring(
            self.env['report'].get_html(doc_id.id, report_name))

    @tools.mute_logger('pysimplesoap.helpers')
    def create_and_send(self, journal_id, partner=None, date=None):
        invoice = self.create_invoice(journal_id=journal_id,
                                      partner=partner, date=date)

        invoice.action_send_to_sunat()

        return invoice

    def cancel_document(self, invoices, reason):
        for invoice in invoices:
            wizard = self.env['invoice.cancel.wizard'].with_context({
                'active_id': invoice.id}).create({
                    'l10n_pe_cancel_reason': reason})
            wizard.button_cancel_reason()
            self.assertTrue(invoice.l10n_pe_edi_serie)
            self.assertTrue(invoice.l10n_pe_edi_correlative)

    def create_credit(self, invoice):
        wizard = self.env['account.invoice.refund'].with_context({
            'active_ids': invoice.ids,
        }).create({
            'description': 'Refund from unit test',
            'filter_refund2': 'refund',
            'l10n_pe_refund_reason': '03',
        })
        wizard.invoice_refund()
        refund_id = self.env['account.invoice'].search([
            ('origin', '=', invoice.number),
            ('type', '=', 'out_refund')])
        refund_id.action_invoice_open()
        return refund_id

    def create_debit(self, invoice):
        wizard = self.env['account.invoice.refund'].with_context({
            'active_ids': invoice.ids,
        }).create({
            'description': 'Debit note from unit test',
            'filter_refund': 'charge',
            'l10n_pe_charge_reason': '02',
        })
        wizard.invoice_refund()
        debit_id = self.env['account.invoice'].search([
            ('origin', '=', invoice.number),
            ('type', '=', 'out_invoice')])
        debit_id.action_invoice_open()
        return debit_id

    def create_wizard_summary(self, date, summary_type):
        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        wizard = wizard_obj.create({'reference_date': date,
                                    'summary_type': summary_type})
        return wizard

    def get_cdr(self, filename, date):
        cdr_expected_path = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'expected_cdr.xml')

        # We read the XML file
        with open(cdr_expected_path) as t_file:
            obj = fromstring(t_file.read())

        # Set the correct date
        self.env['account.invoice'].l10n_pe_edi_xpath(
            obj, '//cbc:ResponseDate')[0]._setText(date)

        # Set it to string
        converted = tostring(obj)

        content = ''
        # Encode the file as expected from the service
        with osutil.tempdir() as temdir, tempfile.TemporaryFile() as t_zip:
            xml_file = os.path.join(temdir, "R-%s.xml" % filename)
            with open(xml_file, "w") as res_file:
                res_file.write(converted)
            osutil.zip_dir(temdir, t_zip, include_dir=False)
            t_zip.seek(0)
            content = base64.b64encode(t_zip.read())
        return content

    def get_custom_statuscode(self, code, filename, date, valid_cdr=True,
                              encoded=True, content=''):
        if encoded:
            content = base64.b64encode(b'Elticketnoexiste')
        if valid_cdr:
            content = self.get_cdr(filename, date)
        return (
            '<S:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envel'
            'ope/" xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"><S:Body'
            '><ns2:getStatusResponse xmlns:ns2="http://service.sunat.gob.pe"><'
            'status><content>%s</content><statusCode>%s</statusCode></status><'
            '/ns2:getStatusResponse></S:Body></S:Envelope>' % (content, code))

    def get_custom_getstatuscdr(self, filename, code="0001",
                                date='2017-01-01', content=True):
        content = self.get_cdr(filename, date) if content else ''
        return ('<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope'
                '/"><S:Body><ns2:getStatusCdrResponse xmlns:ns2="http://servic'
                'e.sunat.gob.pe"><statusCdr><content>%s</content><statusCode>'
                '%s</statusCode></statusCdr></ns2:getStatusCdrResponse>'
                '</S:Body></S:Envelope>' % (content, code))

    def message_check(self, documents, expected='', test='assertIn'):
        assert_to_use = getattr(self, test)
        for document in documents:
            messages = document.message_ids
            message = messages.filtered(lambda r: expected in r.body)
            if test == 'assertIn':
                assert_to_use(expected, message[0].body)
            if test == 'assertFalse':
                assert_to_use(message)

    @staticmethod
    def get_ticket_number_response(ticket):
        """Returns the proper SUNAT response after a summary
        have been sent using sendSummary method from sendBill service,
        this is used for mocked unit testing having this a returning value.
        """
        return (
            '<soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/'
            'soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-'
            'instance" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/'
            'oasis-200401-wss-wssecurity-secext-1.0.xsd"><soap-env:Header/>'
            '<soap-env:Body><br:sendSummaryResponse xmlns:br="http://service.'
            'sunat.gob.pe"><ticket>%s</ticket></br:sendSummaryResp'
            'onse></soap-env:Body></soap-env:Envelope>' % (ticket))

    @staticmethod
    def date_minus(date, minus):
        return datetime.strptime(
            date, tools.DEFAULT_SERVER_DATE_FORMAT) - timedelta(days=minus)

    def create_invoice_different_lines(self, partner, journal_id, lines):
        """This method will receive a dictionary with the partner, quantity,
        price_unit, invoice_line_tax_ids"""
        document = self.env['account.invoice'].with_env(self.env(
            user=self.uid)).create(
                {'partner_id': partner.id,
                 'type': 'out_invoice',
                 'journal_id': journal_id.id,
                 })
        for line in lines:
            document.invoice_line_ids.with_env(self.env(user=self.uid)).create(
                {'product_id': self.product1.id,
                 'uom_id': self.product1.uom_id.id,
                 'quantity': 1,
                 'price_unit': line['price_unit'],
                 'name': self.product1.name,
                 'account_id': self.env.ref('l10n_pe.70111_01').id,
                 'invoice_line_tax_ids': [
                     (6, 0, line['invoice_line_tax_ids'])],
                 'invoice_id': document.id,
                 })
        document._onchange_invoice_line_ids()
        return document

    @staticmethod
    def get_xml_from_zip(b64content, filename):
        with tempfile.TemporaryFile() as zip_file:
            zip_decoded = base64.b64decode(b64content)
            zip_file.write(zip_decoded)
            temp_zip = zipfile.ZipFile(zip_file, 'r')
            return fromstring(temp_zip.read(filename))

    @staticmethod
    def get_custom_response(code, message="-"):
        return '''<S:Envelope
        xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
        <S:Body><S:Fault xmlns:ns4="http://www.w3.org/2003/05/soap-envelope">
        <faultcode>%s</faultcode><faultstring>%s</faultstring>
        </S:Fault></S:Body></S:Envelope>''' % (code, message)

    def check_status(self, documents):
        """ Just pass one document of a series of documents in order to mock
        the response for all of them, for series, put the last one"""
        method_path = ('odoo.addons.l10n_pe_edi.models.account_invoice'
                       '.AccountInvoice._l10n_pe_edi_prepare_and_send')
        for document in documents:
            with mock.patch(method_path) as mock_patch:
                mock_patch.return_value = fromstring(
                    self.get_custom_statuscode(
                        '0', os.path.splitext(
                            document.l10n_pe_edi_summary_id.name)[0],
                        date=document.date_invoice))
                document.l10n_pe_edi_action_get_status_sunat()
