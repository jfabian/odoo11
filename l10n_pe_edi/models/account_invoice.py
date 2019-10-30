# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from __future__ import division

import base64
import logging
import re
import socket
import tempfile
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import groupby
from os.path import join, splitext

from lxml import etree
from lxml.objectify import fromstring

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools import file_open, osutil

from .sunat_errors_dict import l10n_pe_edi_get_error_by_code

_logger = logging.getLogger(__name__)

try:
    from signxml import XMLSigner
    from num2words import num2words
    from pdf417gen import encode, render_image
    from pysimplesoap.client import SoapClient, SoapFault
    from httplib2 import ServerNotFoundError
    from httplib import ResponseNotReady

except ImportError as err:
    _logger.debug(err)
UBLPE_TEMPLATE = 'l10n_pe_edi.UBLPE-%s-%s'
UBLPE_XSD = 'l10n_pe_edi/data/%s/maindoc/UBLPE-%s-%s.xsd'

L10N_PE_EDI_NS = {
    'cbc': ('urn:oasis:names:specification:ubl:schema:xsd:'
            'CommonBasicComponents-2'),
    'sac': ('urn:sunat:names:specification:ubl:peru:schema:'
            'xsd:SunatAggregateComponents-1'),
    'cac': ('urn:oasis:names:specification:ubl:schema:xsd:'
            'CommonAggregateComponents-2'),
    'ccts': 'urn:un:unece:uncefact:documentation:2',
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
    'ext': ('urn:oasis:names:specification:ubl:schema:xsd:'
            'CommonExtensionComponents-2'),
    'qdt': 'urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2',
    'udt': ('urn:un:unece:uncefact:data:specification:'
            'UnqualifiedDataTypesSchemaModule:2'),
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'ar': ('urn:oasis:names:specification:ubl:schema:'
           'xsd:ApplicationResponse-2'),
}
L10N_PE_EDI_JOURNAL_CODES = ['FAC', 'BOL', 'GR']


def get_xsd_template_names(doc_type, version):
    """Based on document type and PSE xml version, it builds the template
    name and XSD filename to be used getting also the document name.
    This use UBLPE_TEMPLATE, UBLPE_XSD, they are global variables.
    :param doc_type: Document type based on SUNAT Catalog No. 1
    :param version: Version of XML documents
    :return: a tuple containing: template name to be loaded as xml_id, XSD
    file path and document name to be replaced after xml gets rendered
    """
    doc_code_names = {'07': 'CreditNote', '08': 'DebitNote',
                      '01': 'Invoice', '03': 'Invoice',
                      'RA': 'VoidedDocuments', 'RC': 'SummaryDocuments'}
    doc_name = doc_code_names.get(doc_type)
    template_name = UBLPE_TEMPLATE % (doc_name, version.replace('.', ''))
    xsd_name = UBLPE_XSD % (version, doc_name, version)
    return (template_name, xsd_name, doc_name)


def create_list_html(array):
    """Convert an array of string to a html list.
    :param array: A list of strings
    :return: an empty string if not array, an html list otherwise
    """

    if not array:
        return ""

    msg = ""
    for item in array:
        msg += "<li>" + item + "</li>"
    return "<ul>" + msg + "</ul>"


def check_with_xsd(tree_or_str, xsd_path):
    """Taken from Vauxoo/odoo:saas-14 (https://goo.gl/UcyvXC) until it gets
    ported to branch 10.0
    """
    if not isinstance(tree_or_str, etree._Element):
        tree_or_str = etree.fromstring(tree_or_str)
    xml_schema_doc = etree.parse(file_open(xsd_path))
    xsd_schema = etree.XMLSchema(xml_schema_doc)
    try:
        xsd_schema.assertValid(tree_or_str)
    except etree.DocumentInvalid, xml_errors:
        raise UserError('\n'.join([e.message for e in xml_errors.error_log]))


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('journal_id', 'refund_invoice_id')
    def _compute_l10n_pe_document_type(self):
        """Based on Catalog no. 1 of SUNAT, documents have code related
        that you can see on https://goo.gl/rGedAU. The codes identify the
        documents in the SUNAT systems
        """

        invoice = self.filtered(lambda r: r.l10n_pe_edi_is_required())
        # Factura
        invoice.filtered(lambda r: r.journal_id.code == 'FAC' and
                         r.type == 'out_invoice' and not r.refund_invoice_id
                         ).update({'l10n_pe_document_type': '01'})

        # Boleta
        invoice.filtered(lambda r: r.journal_id.code == 'BOL' and
                         r.type == 'out_invoice' and not r.refund_invoice_id
                         ).update({'l10n_pe_document_type': '03'})

        # Guía de Remisión
        invoice.filtered(lambda r: r.journal_id.code == 'GR' and
                         r.type == 'out_invoice' and not r.refund_invoice_id
                         ).update({'l10n_pe_document_type': '09'})

        # Nota de Crédito
        invoice.filtered(lambda r: r.type == 'out_refund' and
                         r.refund_invoice_id
                         ).update({'l10n_pe_document_type': '07'})

        # Nota de Débito
        invoice.filtered(lambda r: r.type == 'out_invoice' and
                         r.refund_invoice_id
                         ).update({'l10n_pe_document_type': '08'})

    l10n_pe_document_type = fields.Selection([
        ('01', 'FACTURA'),
        ('03', 'BOLETA DE VENTA'),
        ('09', 'GUIA DE REMISION REMITENTE'),
        ('07', 'NOTA DE CREDITO'),
        ('08', 'NOTA DE DEBITO'),
    ], compute="_compute_l10n_pe_document_type", store=True)
    l10n_pe_refund_reason = fields.Selection([
        ('01', 'Anulación de la operación'),
        ('02', 'Anulación por error en el RUC'),
        ('03', 'Corrección por error en la descripción'),
        ('04', 'Descuento global'),
        ('05', 'Descuento por ítem'),
        ('06', 'Devolución total'),
        ('07', 'Devolución por ítem'),
        ('08', 'Bonificación'),
        ('09', 'Disminución en el valor'),
    ], help='It contains all possible values for cbc:ResponseCode',
        string="Reason for the credit note")
    l10n_pe_charge_reason = fields.Selection(
        [('01', 'Intereses por mora'),
         ('02', 'Aumento en el valor')],
        default='01', string='Debit Reason', help='Debit note reason')

    @api.depends('journal_id', 'origin')
    def _compute_amount_value_type(self):
        """Used in Daily Summary. When
        for amount types from taxes point of view
        (whether it gets affected or not).
        Please refer to following xls file : https://goo.gl/FM3F7m
        that indicates the columns K,L,M are amounts related to the voucher,
        and if there is no value, it is required to be zero.
        This catalog no 11 can be found on https://goo.gl/rGedAU
            '01' - 'Gravado'
            '02' - 'Exonerado'
            '03' - 'Inafecto'
            '04' - 'Exportación'
            '05' - 'Gratuitas'
        :return: the corresponding code for the amount type
        ..todo :: It is required to include full values computations to be
        taken from invoice for codes 02-05
        """
        self.update({'l10n_pe_amount_value_type': '01'})

    l10n_pe_amount_value_type = fields.Selection([
        ('01', 'Gravado'),
        ('02', 'Exonerado'),
        ('03', 'Inafecto'),
        ('04', 'Exportación'),
        ('05', 'Gratuitas'),
    ], compute='_compute_amount_value_type', store=True)

    @api.depends('journal_id', 'origin')
    def _compute_additional_monetary_total_values(self):
        """Gets a total value in invoice and relates it to the code
        required by SUNAT. This represents the catalog no. 14
        :return: a value with the corresponding code for the amount
        """
        self.update({'l10n_pe_monetary_total': '1001'})

    l10n_pe_monetary_total = fields.Selection(
        [
            ('1001', 'Total valor de venta - operaciones gravadas'),
            ('1002', 'Total valor de venta - operaciones inafectas'),
            ('1003', 'Total valor de venta - operaciones exoneradas'),
            ('1004', 'Total valor de venta - Operaciones gratuitas'),
            ('1005', 'Sub total de venta'),
            ('2001', 'Percepciones'),
            ('2002', 'Retenciones'),
            ('2003', 'Detracciones'),
            ('2004', 'Bonificaciones'),
            ('2005', 'Total descuentos')],
        help="Otros conceptos tributarios",
        compute='_compute_additional_monetary_total_values', store=True)

    @api.model
    def get_additional_property(self, code):
        """Gets valid value depending on the code
        received through arguments in order to meet SUNAT catalog 15.
        for now is:
            - 1000 : Document amount in words
        This represents the catalog no 15 for SUNAT and can
        be found https://goo.gl/rGedAU
        :param code: returns the value for the expected code, the valid code
        :return: a string having the legend
        """
        value = False
        if code == '1000':
            value = str(self.amount_total)
            part_int, part_dec = value.split('.')
            value = num2words(float(part_int), lang='es')
            currency_name = self.with_context({
                'lang': 'es'
            }).currency_id.print_on_check
            value += ' CON %s/100 %s' % (part_dec, currency_name)
            value = value.upper()
        return value

    l10n_pe_edi_ublpe = fields.Binary(
        string="ublpe content", copy=False, readonly=True,
        compute="_compute_ublpe_values",
        help="The ublpe xml content encoded in base64")
    l10n_pe_edi_ublpe_name = fields.Char(
        string="ublpe name", copy=False, readonly=True,
        help="The attachment name of the ublpe")
    l10n_pe_edi_pse_status = fields.Selection([
        ('retry', 'Retry'),
        ('to_sign', 'To sign'),
        ('signed', 'Signed'),
        ('valid', 'Valid'),
        ('to_cancel', 'To cancel'),
        ('with_error', 'Processed with errors'),
        ('in_process', 'In process'),
        ('to_be_cancelled', 'To be cancelled'),
        ('cancelled', 'Cancelled')], string="Document Status",
        help="Refers to the status of the invoice in SUNAT",
        readonly=True, copy=False)

    @api.model
    def l10n_pe_edi_retrieve_attachments(self):
        """Retrieve all the ublpe attachments generated for this invoice.

        :return: An ir.attachment recordset
        """
        self.ensure_one()
        if not self.l10n_pe_edi_ublpe_name:
            return []
        domain = [
            ('res_id', '=', self.id),
            ('res_model', '=', self._name),
            ('name', '=', self.l10n_pe_edi_ublpe_name)]
        return self.env['ir.attachment'].search(domain)

    @api.model
    def l10n_pe_edi_retrieve_last_attachment(self):
        if not self.l10n_pe_edi_is_required():
            return None
        attachment_ids = self.l10n_pe_edi_retrieve_attachments()
        return attachment_ids[0] if attachment_ids else None

    @api.multi
    @api.depends('l10n_pe_edi_ublpe_name')
    def _compute_ublpe_values(self):
        """Fill the invoice fields from the ublpe values"""

        for invoice in self:
            if not invoice.l10n_pe_edi_is_required():
                return

            attachment_id = invoice.l10n_pe_edi_retrieve_last_attachment()
            if not attachment_id:
                continue
            # At this moment, the attachment contains the file size in its
            # 'datas' field because to save some memory, the attachment will
            # store its data on the physical disk. To avoid this problem, we
            # read the 'datas directly on the disk'
            datas = attachment_id._file_read(attachment_id.store_fname)
            invoice.l10n_pe_edi_ublpe = datas

            # TODO: if already signed, extract uuid
            # TODO: get the rest of fields to be computed

    @api.multi
    def l10n_pe_edi_get_pse_version(self):
        """Returns the ublpe version from database parameters.
        By default is 2.0
        :return: version of document, if not exists 2.0 will be
        returned"""
        version = self.env['ir.config_parameter'].sudo().get_param(
            'l10n_pe_edi_ublpe_version', '2.0')
        return version

    @api.model
    def l10n_pe_edi_get_xml_etree(self, ublpe=None, file_fmt="%(name)s.xml",
                                  file_name=False):
        """Get an objectified tree representing the ublpe
        if the ublpe is not specified, retrieve it from the attachment.

        :param ublpe: the ublpe as string
        :param file_fmt: format name for the file to be parsed
        :param file_name: name of file to be read
        :return: An objectified tree if valid, False in counter case
        """
        self.ensure_one()
        if not self.l10n_pe_edi_is_required():
            return
        file_name = file_fmt % {
            'name': splitext(file_name or self.l10n_pe_edi_ublpe_name)[0]}
        ublpe = ublpe or self.l10n_pe_edi_ublpe
        with tempfile.TemporaryFile() as zip_file:
            zip_decoded = base64.b64decode(ublpe)
            zip_file.write(zip_decoded)
            try:
                temp_zip = zipfile.ZipFile(zip_file, 'r')
                file_name = [name for name in temp_zip.namelist()
                             if name.lower() == file_name.lower()]
                ublpe = temp_zip.read(file_name[0])
            except (zipfile.BadZipfile, KeyError):
                return False
        return fromstring(ublpe)

    @api.multi
    def _l10n_pe_edi_create_ublpe_values(self):
        """Create taxes values to fill the UBLPE template,
        Those taxes summary adopt the certain values. please refer to pdf page
        40 in https://goo.gl/eh2ZyT (invoice manual)
        """
        self.ensure_one()
        if not self.l10n_pe_edi_is_required():
            return
        precision = self.env['decimal.precision'].precision_get('Account')
        values = {
            'record': self,
            'company': self.company_id,
            'date': self.date_invoice,
            'free_sale': not self.amount_untaxed,
        }
        values['taxes'] = [{
            'currency': self.currency_id.name,
            'amount': tools.float_round(self.l10n_pe_edi_total_igv, precision),
            'edi_id': '1000',
            'name': 'IGV',
            'code': 'VAT',
        }, {
            'currency': self.currency_id.name,
            'amount': tools.float_round(self.l10n_pe_edi_total_isc, precision),
            'edi_id': '2000',
            'name': 'ISC',
            'code': 'EXC',
        }, {
            'currency': self.currency_id.name,
            'amount': tools.float_round(self.l10n_pe_edi_total_otros,
                                        precision),
            'edi_id': '9999',
            'name': 'OTROS',
            'code': 'OTH',
        }]
        return values

    @api.multi
    def invoice_print(self):
        self.ensure_one()
        if not self.l10n_pe_edi_is_required():
            return super(AccountInvoice, self).invoice_print()
        self.sent = True
        return self.env['report'].get_action(
            self, 'l10n_pe_edi.l10n_pe_edi_report_invoice')

    @api.multi
    def _l10n_pe_edi_create_ublpe(self):
        self.ensure_one()
        qweb = self.env['ir.qweb']

        values = self._l10n_pe_edi_create_ublpe_values()
        doc_type = self.l10n_pe_document_type

        if self.l10n_pe_edi_error_message:
            raise UserError(self.l10n_pe_edi_error_message)

        # -----------------------
        # Create the EDI document
        # -----------------------
        version = self.l10n_pe_edi_get_pse_version()
        xml_template_name, xsd_filename, doc_name = \
            get_xsd_template_names(doc_type, version)

        # Compute ublpe
        ublpe = qweb.render(xml_template_name, values=values)

        # Replace back colons in namespaces
        ublpe = ublpe.replace('__', ':')

        # Include xml namespace to indicate Invoice as root element of xml doc
        replace_dict = {'dn': doc_name}
        ublpe = ublpe.replace(
            '<%(dn)s' % replace_dict,
            '<%(dn)s xmlns="urn:oasis:names:specification:ubl:schema:xsd'
            ':%(dn)s-2"' % replace_dict)

        tree = fromstring(ublpe)

        # Check with xsd
        try:
            check_with_xsd(tree, xsd_filename)
        except UserError as e:
            return {'error': _('The ublpe generated is not valid') +
                    create_list_html(e.name.split('\n'))}
        return {'ublpe': etree.tostring(tree, xml_declaration=True,
                                        encoding='ISO-8859-1')}

    @api.multi
    def _l10n_pe_edi_call_service(self, service_type):
        """Call the right methods according to the sunat
        method antes service pass as parameter.
        : param service_type: sign or cancel
        """
        comp_x_records = groupby(self, lambda r: r.company_id)
        for company_id, records in comp_x_records:
            pse_name = company_id.l10n_pe_edi_pse
            if not pse_name:
                continue

            # Get the informations about the PSE
            pse_info_func = '_l10n_pe_edi_%s_info' % pse_name
            service_func = '_l10n_pe_edi_%s_%s' % (pse_name, service_type)
            pse_info = getattr(self, pse_info_func)(company_id, service_type)

            # Call the service with invoices
            for record in records:
                getattr(record, service_func)(pse_info)

    @api.multi
    def _l10n_pe_edi_local_info(self, company_id, service_type):
        return {
            'url': False,
            'username': False,
            'password': False,
            'certificate': (company_id.l10n_pe_edi_certificate_ids.sudo().
                            get_valid_certificate())
        }

    l10n_pe_cancel_reason = fields.Char(
        string="Cancel Reason", copy=False, readonly=True,
        help="Reason given by the user to cancel this move"
    )

    @staticmethod
    def l10n_pe_edi_xpath(xml, xpath):
        """Given a XML and a XPATH this method will return a value
        """
        value = xml.xpath(xpath, namespaces=L10N_PE_EDI_NS)
        return value

    @api.multi
    def _l10n_pe_edi_local_sign(self, pse_info):
        for inv in self:
            attachment = inv.l10n_pe_edi_retrieve_last_attachment()
            encoded_file = attachment.datas
            root = self.l10n_pe_edi_get_xml_etree(ublpe=encoded_file)
            xml_signed = inv._l10n_pe_edi_sign_xml(root)
            if xml_signed is not None:
                xml_signed = etree.tostring(xml_signed, xml_declaration=True,
                                            encoding='ISO-8859-1')
            inv._l10n_pe_edi_post_sign_process(xml_signed)

    def l10n_pe_edi_create_zipfile(self, filename, xml_signed):
        """Creating a zip file as attachment in the chatter.

        This method is used as a requirement for the SUNAT in sending files to
        their servers. We replace an existing XML file in the chatter
        attachment with this zip.
        In page 10 of this document https://goo.gl/wShdQM says that the zip
        must contain a dummy/ folder, but in the samples we got that this
        is deprecated, so is not included in this method.
        """
        attachment = False
        attachment_name = "%s.zip" % filename
        ctx = self.env.context.copy()
        ctx.pop('default_type', False)
        with osutil.tempdir() as temdir, tempfile.TemporaryFile() as t_zip:
            xml_file = join(temdir, "%s.xml" % filename)
            with open(xml_file, "w") as res_file:
                res_file.write(xml_signed)
            osutil.zip_dir(temdir, t_zip, include_dir=False)
            t_zip.seek(0)
            encoded = base64.b64encode(t_zip.read())
            attachment = self.env['ir.attachment'].with_context(ctx).create({
                'datas': encoded,
                'res_model': self._name,
                'mimetype': 'application/zip',
                'name': attachment_name,
                'datas_fname': attachment_name,
                'l10n_pe_edi_sunat_file': True,
            })
        return attachment

    @api.multi
    def _l10n_pe_edi_post_sign_process(self, xml_signed, code=None, msg=None):
        """Post process the results of the sign service.
        :param xml_signed: the xml signed datas codified in base64
        :param code: an eventual error code
        :param msg: an eventual error msg
        """
        self.ensure_one()
        if xml_signed:
            body_msg = _('The sign service has been called with success')
            # Update the pse status
            self.l10n_pe_edi_pse_status = 'signed'
            self.l10n_pe_edi_ublpe = xml_signed

            attachment = self.l10n_pe_edi_retrieve_last_attachment()
            filename = splitext(attachment.datas_fname)[0]
            with osutil.tempdir() as temdir, tempfile.TemporaryFile() as t_zip:
                xml_file = join(temdir, "%s.xml" % filename)
                with open(xml_file, "w") as res_file:
                    res_file.write(xml_signed)
                osutil.zip_dir(temdir, t_zip, include_dir=False)
                t_zip.seek(0)
                encoded = base64.b64encode(t_zip.read())
                attachment.write({'datas': encoded})
            self.l10n_pe_edi_ublpe_name = attachment.datas_fname

            post_msg = [_("The content of the attachment has been updated")]
        else:
            body_msg = _("The sign service requested failed")
            post_msg = []
        if code:
            post_msg.extend([_("Code: ") + str(code)])
        if msg:
            post_msg.extend([_("Message: ") + msg])

        self.message_post(
            body=body_msg + create_list_html(post_msg),
            subtype="account.mt_invoice_validated")

    def _l10n_pe_edi_sign(self):
        """Call the sign service with records that can be signed.
        """
        records = self.search([
            ('l10n_pe_edi_pse_status', 'not in', ['signed', 'to_cancel',
                                                  'cancelled', 'retry']),
            ('id', 'in', self.ids)])
        records._l10n_pe_edi_call_service('sign')

    @api.multi
    def _l10n_pe_edi_retry(self):
        """Generate the UBLPE zip file attachment
        """

        for invoice in self:
            # Render the xml template
            ublpe_values = invoice._l10n_pe_edi_create_ublpe()
            error = ublpe_values.pop('error', None)
            ublpe = ublpe_values.pop('ublpe', None)

            if error:
                invoice.l10n_pe_edi_pse_status = 'retry'
                invoice.message_post(body=error,
                                     subtype="account.mt_invoice_validated")
                continue

            # XML template has been successfully rendered
            invoice.l10n_pe_edi_pse_status = 'to_sign'
            document_number = invoice.number

            # Create ZIP file with the signed XML
            filename = ('%s-%s-%s' % (
                invoice.company_id.partner_id.l10n_pe_vat_number,
                invoice.l10n_pe_document_type,
                document_number)).replace('/', '')

            ctx = self.env.context.copy()
            ctx.pop('default_type', False)

            attachment_id = invoice.l10n_pe_edi_create_zipfile(filename, ublpe)
            attachment_id.write({'res_id': invoice.id})
            invoice.l10n_pe_edi_ublpe_name = attachment_id.datas_fname
            # Post in chatter the attachment expected
            invoice.message_post(
                body=_("UBLPE document generated (it may not be signed)"),
                attachment_ids=attachment_id.ids,
                subtype="account.mt_invoice_validated")
            invoice._l10n_pe_edi_sign()

    def _l10n_pe_edi_sign_xml(self, root, company=None):
        company = company or self.company_id
        certificate = (company.l10n_pe_edi_certificate_ids.sudo().
                       get_valid_certificate())
        pem_key = certificate.get_pem_key(certificate.content,
                                          certificate.password)
        pem_cert = certificate.get_pem_cert(certificate.content,
                                            certificate.password)
        xml_signed = XMLSigner(
            digest_algorithm='sha1', signature_algorithm='rsa-sha1',
            c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"
        ).sign(root, key=pem_key, cert=pem_cert)
        self.l10n_pe_edi_xpath(
            xml_signed, '//ext:UBLExtensions/ext:UBLExtension/ext:'
            'ExtensionContent/ds:Signature')[0].attrib['Id'] = 'SignVX'
        return xml_signed

    @api.multi
    def l10n_pe_edi_is_required(self):
        self.ensure_one()
        return (self.type in ('out_invoice', 'out_refund') and
                self.company_id.country_id == self.env.ref('base.pe'))

    @api.multi
    def invoice_validate(self):
        """Generate ublpe documents attachments for peruvian companies when
        validated
        """
        for invoices in self.filtered(lambda r: r.l10n_pe_edi_is_required() and
                                      (r.number or r.move_name)):
            if invoices.journal_id.code not in L10N_PE_EDI_JOURNAL_CODES:
                message = _('The code in the journal is not valid for SUNAT '
                            'standards, please use %s instead') % ','.join(
                                L10N_PE_EDI_JOURNAL_CODES)
                invoices.message_post(body=message, message_type='comment')
                continue

            invoices.l10n_pe_edi_ublpe_name = ('%s-%s-%s.xml' % (
                invoices.company_id.partner_id.l10n_pe_vat_number,
                invoices.l10n_pe_document_type,
                invoices.move_id.name,)).replace('/', '')
            invoices.date_invoice = \
                fields.Date.from_string(
                    self.env['l10n_pe_edi.certificate'].
                    get_pe_current_datetime().strftime("%Y-%m-%d"))
            invoices._l10n_pe_edi_retry()
        return super(AccountInvoice, self).invoice_validate()

    @api.multi
    def action_invoice_cancel(self):
        """Cancel the ublpe attachments for peruvian companies when cancelled
        """
        not_allow = self.env['account.invoice']
        if (not self.env.user.has_group(
           'l10n_pe_edi.res_group_super_user_manager')):
            today = self.env[
                'l10n_pe_edi.certificate'].get_pe_current_datetime()
            limit_date_str = fields.datetime.strftime(
                (today - timedelta(days=7)), tools.DEFAULT_SERVER_DATE_FORMAT)

            not_allow = self.filtered(
                lambda r: r.l10n_pe_edi_is_required() and not
                (not r.date_invoice or
                    r.date_invoice >= limit_date_str or
                    r.l10n_pe_edi_pse_status == 'with_error'))
            for invoice in not_allow:
                invoice.message_post(
                    subject=_('Error cancelling your document'),
                    body=_("This document can't be cancelled, it's out of the "
                           "limit time and has no error. Create a credit a"
                           " note instead"), message_type='comment')
        (self - not_allow)._l10n_pe_edi_cancel()
        not_allow |= self.filtered(lambda r:
                                   r.l10n_pe_document_type == '01' and
                                   not r.l10n_pe_edi_cdr_date and
                                   r.l10n_pe_edi_pse_status == 'signed')
        return super(AccountInvoice, self - not_allow).action_invoice_cancel()

    @api.multi
    def l10n_pe_edi_update_pse_status(self):
        """Synchronize both systems: Odoo & PSE if the invoices need to be
        signed or cancelled.
        """
        for record in self:
            if record.l10n_pe_edi_pse_status == 'to_sign':
                record._l10n_pe_edi_sign()
            elif record.l10n_pe_edi_pse_status == 'retry':
                record._l10n_pe_edi_retry()
            elif record.l10n_pe_edi_pse_status in ['signed', 'with_error']:
                record.action_send_to_sunat()

    @api.multi
    def _l10n_pe_edi_cancel(self):
        """Call the cancel service with records that can be signed
        """
        invoices = self.search([
            ('l10n_pe_edi_pse_status', 'in',
             ['to_sign', 'signed', 'retry', 'valid', 'in_process']),
            ('id', 'in', self.ids), ('move_name', '!=', False)])
        for invoice in invoices:
            if not invoice.l10n_pe_edi_is_required():
                continue
            if (invoice.l10n_pe_edi_pse_status == 'signed' and
               invoice.state in ['open', 'paid'] and
               invoice.l10n_pe_document_type == '01'):
                invoice.l10n_pe_edi_update_pse_status()
                if not invoice.l10n_pe_edi_cdr_date:
                    continue

            invoice.update({
                'l10n_pe_edi_pse_status': 'to_cancel',
                'l10n_pe_edi_ticket_number': False,
                'l10n_pe_edi_summary_id': False,
            })
        cron_voided = self.env.ref('l10n_pe_edi.ir_cron_send_voided_documents')
        cron_voided.sudo().nextcall = fields.datetime.strptime(
            fields.Datetime.now(), tools.DEFAULT_SERVER_DATETIME_FORMAT) + (
                timedelta(minutes=15))

    def l10n_pe_edi_call_sunat_service(self, client, name, params):
        """Call a SUNAT webservice with the parameters that the service method
        needs.
        If a SoapFault exception is raised: An XSL validation wasn't met and
        it gets registered in the invoice chatter.
        If an AttributeError exception is raised: The service method does not
        exists, it will be logged.
        :params client: wsdl client with credentials
        :params name: service method name to be called
        :params params: parameters required to call the service method.
        """
        try:
            service = getattr(client, name)
            service(**params)
            return fromstring(client.xml_response)
        except SoapFault as ex:
            return {
                'error': {
                    'subject': _('Error received from SUNAT'),
                    'message': _('Code: %s<br/>Message: %s') %
                    (ex.faultcode, ex.faultstring),
                }
            }
        except AttributeError:
            _logger.error("Service '%s' does not exist", name)
            return {
                'error': {
                    'subject': _('Service not implemented'),
                    'message': _(
                        "The service '%s' you are trying to consume is not "
                        "implemented yet or it does not exists.") % name
                }
            }

        except BaseException:
            return {
                'error': {
                    'subject': _('General error cached'),
                    'message': _(
                        "We got a problem while processing your request "
                        "please, stand by and try again.")
                }
            }

    def l10n_pe_edi_sunat_send_bill(self, client, vals):
        """It represents the method sendBill in SUNAT services.
        :param client: WSDL client
        :param vals: parameters values
        :return: The value returned is a acceptance/rejection proof, that is a
        zip file with a xml inside of it.
        """
        return self.l10n_pe_edi_call_sunat_service(client, 'sendBill', vals)

    def l10n_pe_edi_sunat_send_summary(self, client, vals):
        """It represents the method sendSummary in SUNAT services. Used for:
            - Resumen Diario de Boletas
            - Comunicación de Baja
        :param client: WSDL client
        :param vals: parameters values
        :return: The value returned is a ticket number generated by SUNAT that
        represent a service for document processing.
        """
        return self.l10n_pe_edi_call_sunat_service(client, 'sendSummary', vals)

    def l10n_pe_edi_sunat_send_pack(self, client, vals):
        """It represents the method sendPack in SUNAT services. Used for:
            - Lote de Facturas
        :param client: WSDL client
        :param vals: parameters values
        :return: The value returned is a ticket number generated by SUNAT.
        """
        return self.l10n_pe_edi_call_sunat_service(client, 'sendPack', vals)

    def l10n_pe_edi_sunat_get_status(self, client, vals):
        """It represents the method getStatus in SUNAT services.
        :param client: WSDL client
        :param vals: parameters values
        """
        return self.l10n_pe_edi_call_sunat_service(client, 'getStatus', vals)

    def l10n_pe_edi_sunat_get_status_cdr(self, client, vals):
        """It represents the method getStatusCdr in SUNAT services.
        :param client: WSDL client
        :param vals: parameters values
        """
        return self.l10n_pe_edi_call_sunat_service(
            client, 'getStatusCdr', vals)

    @api.multi
    def l10n_pe_edi_action_get_status_cdr_sunat(self):
        """Obtain the CDR response from SUNAT for the document, this
        functionality is valid for electronic invoices and related notes
        (debit and credit), document types 01, 07 and 08, respectively that
        begins with 'F' (based on code 0010, see https://goo.gl/iJej7x)
        """
        for invoice in self:
            response = invoice._l10n_pe_edi_prepare_and_send(
                service_name='get_status_cdr', company=invoice.company_id)

            if 'error' in response:
                res_error = response['error']
                invoice.message_post(subject=res_error['subject'],
                                     body=res_error['message'],
                                     message_type='comment')
                continue

            cdr_code = response.xpath('//statusCdr/statusCode')
            cdr_code = cdr_code[0].text if cdr_code else ''
            msg = l10n_pe_edi_get_error_by_code(cdr_code)
            # Save that response here, for the record, not the CDR
            cdr_response = ''
            try:
                cdr_response = response.xpath('//content')[0]
            except IndexError:
                invoice.message_post(body=_(
                    "There is no //content label in the response, please "
                    "check in SUNAT if this document has an expected state,"
                    " later, report an issue to the developer team."))
            if cdr_response:
                item = invoice.l10n_pe_edi_get_xml_etree(
                    cdr_response[0].text, file_fmt="R-%(name)s.xml")
                cdr_response_code = invoice.l10n_pe_edi_xpath(
                    item,
                    '//cac:DocumentResponse/cac:Response/cbc:ResponseCode')[0]
                if cdr_response_code.text != '0':
                    file_name = 'R-%s' % (
                        splitext(invoice.l10n_pe_edi_ublpe_name)[0])
                    msg = l10n_pe_edi_get_error_by_code(cdr_response_code.text)
                    invoice._l10n_pe_edi_sunat_save_cdr(
                        filename=file_name, content=cdr_response)
                    status = 'with_error'
            try:
                cdr_code = int(cdr_code)
            except ValueError:
                msg = _('SUNAT response is: %s' %
                        cdr_code)
                continue
            finally:
                invoice.message_post(subject=_('CDR Response'), body=msg,
                                     message_type='comment')

            if cdr_code == 2 or cdr_code >= 5:
                status = 'with_error'
            elif cdr_code == 3:
                status = 'cancelled'
            elif cdr_code in (1, 4):
                status = 'to_cancel' if invoice.state == 'cancel' else 'valid'
            invoice.l10n_pe_edi_pse_status = status

            cdr_content = response.xpath('//statusCdr/content')
            cdr_content = cdr_content[0].text if cdr_content else False

            if not cdr_content:
                continue

            # Save SUNAT CDR into a new attachment
            attachment = invoice.l10n_pe_edi_retrieve_last_attachment()
            cdr_name = 'CDR-%s' % attachment.name
            cdr_attachment = invoice._l10n_pe_edi_sunat_save_cdr(
                filename=cdr_name, content=cdr_content)
            invoice.message_post(
                body=_("A CDR have been recovered for %s") % attachment.name,
                attachment_ids=cdr_attachment.ids, message_type='comment')

            if status != 'valid':
                continue

            # get received response and update CDR date
            cdr = invoice.l10n_pe_edi_get_xml_etree(
                ublpe=cdr_content, file_fmt="R-%(name)s.xml",
                file_name=attachment.name)
            invoice._l10n_pe_edi_update_cdr_date(cdr_name, cdr)

    def _l10n_pe_edi_prepare_and_send(self, service_name, attachment=None,
                                      ticket_no=None, company=None):
        """Prepare and send to SUNAT documents based on method used.
        :param service_name: Method name to be used to send/consult to SUNAT
        :param attachment: In case a file needs to be sent, this attachment
        will be converted to base64 and sent to SUNAT.
        :param ticket_no: In case the method will be consulting the status in
        SUNAT for a document, this will be set.
        :param company: this company contains login credentials and url to be
        used to communicate with SUNAT
        :returns: In case of successful communication with the SUNAT
        webservices a xml response format will be returned, in counter case for
        a local issue, network failures or credentials errors a dict with the
        error will be returned to be informed to the user.
        """
        zip_file, zip_name = None, None
        if attachment:
            zip_file = attachment.datas
            zip_name = attachment.datas_fname

        company = company or self.company_id

        username = company.l10n_pe_edi_sunat_username
        password = company.l10n_pe_edi_sunat_password

        # Based on the method name the web service url to be used changes.
        # DEAR FUTURE ME: This is probably not the best way to accomplish this
        url_field = 'sunat_'
        if service_name == 'get_status_cdr':
            url_field = 'bill_consult_'
        try:
            sunat_url = getattr(company, 'l10n_pe_edi_%surl' % url_field)
        except AttributeError:
            sunat_url = False

        if not (username and password and sunat_url):
            return {'error': {
                'subject': _('Error with credentials'),
                'message': _("SUNAT SOL Parameters haven't been set "
                             "correctly, please check that all web service "
                             "addresses and SOL credentials are set "
                             "in Accounting > Settings")
            }}
        try:
            client = SoapClient(wsdl=sunat_url, soap_ns='soapenv', ns='ser',
                                trace=logging.INFO)
        except (ServerNotFoundError, ResponseNotReady) as message:
            content = _('Seems that you are having trouble with the network\
                <br/>Please try again later')
            _logger.error("Network connection error")
            return {'error': {
                'subject': _('Error connecting to server'),
                'message': _('Message: %s<br/>%s') % (message, content)
            }}

        except socket.error as e:
            return {
                'error': {
                    'subject': _('Conection reset by peer'),
                    'message': _(
                        "The service you are trying to consume is not "
                        "responding, it returned this message: %s") % (e)
                }
            }

        except BaseException:
            return {
                'error': {
                    'subject': _('General error cached'),
                    'message': _(
                        "We got a problem while processing your request "
                        "please, stand by and try again.")
                }
            }

        client['wsse:Security'] = {
            'wsse:UsernameToken': {
                'wsse:Username': username,
                'wsse:Password': password,
            }
        }

        vals = {
            'send_bill': {'fileName': zip_name, 'contentFile': zip_file},
            'send_summary': {'fileName': zip_name, 'contentFile': zip_file},
            'send_pack': {'fileName': zip_name, 'contentFile': zip_file},
            'get_status': {'ticket': ticket_no},
            'get_status_cdr': {
                'rucComprobante':
                self.company_id.partner_id.l10n_pe_vat_number,
                'tipoComprobante': self.l10n_pe_document_type,
                'serieComprobante': self.l10n_pe_edi_serie,
                'numeroComprobante': self.l10n_pe_edi_correlative
            }
        }
        params = vals.get(service_name)
        getattr(self, 'l10n_pe_edi_sunat_%s' % service_name)(client, params)
        try:
            return fromstring(client.xml_response)
        except etree.XMLSyntaxError:
            return {
                'error': {
                    'subject': _('No XML as response'),
                    'message': _("The service you are trying to consume is"
                                 " not responding with an xml")
                }
            }

    def _l10n_pe_edi_sunat_save_cdr(self, filename, content, invoice_ids=None):
        invoice_id = False
        if invoice_ids and len(invoice_ids) == 1:
            invoice_id = invoice_ids.id
        ctx = self.env.context.copy()
        ctx.pop('default_type', False)
        attachment = self.env['ir.attachment'].with_context(ctx).create({
            'datas': content,
            'mimetype': 'application/zip',
            'res_id': invoice_id,
            'res_model': self._name if invoice_id else False,
            'name': filename,
            'datas_fname': filename,
            'l10n_pe_edi_sunat_file': True,
        })

        if invoice_ids:
            invoice_ids.message_post(body=_("CDR Received"),
                                     attachment_ids=attachment.ids,
                                     subtype="account.mt_invoice_validated",
                                     message_type='comment')
        return attachment

    @staticmethod
    def l10n_pe_edi_get_error(response):
        """Detect is there is an error when sending documents to SUNAT.
        :param response: Response received from SUNAT request or local errors
        for custom validations to avoid rejections.
        :return: In any of the following cases, a tuple with title and message
        of the error and a value to know the kind of error detected:
        - If the response contains 'error' key, the error message is based on
        locally errors and there no document sent to SUNAT
        - If any error message is received, it will be returned. Also based on
        type of error:
            - >=0100<=1999 It was not received
            -       >=4000 Valid with observations
            - Any other value is considered as rejected
        - If no error is received, all values will be false.
        """
        if 'error' in response:
            res_error = response['error']
            return res_error['subject'], res_error['message'], 'not_sent'

        faultcode = response.xpath('//faultcode')
        faultcode = faultcode[0].text if faultcode else ''
        faultstring = response.xpath('//faultstring')
        faultstring = faultstring[0].text if faultstring else ''
        # Sometimes the return code is within a string like
        # soap-env:Server.200 or soap-env:Client.2072
        match = re.search(r"soap-env:(Server|Client)\.(\d+)", faultcode)
        if match:
            faultcode = match.group(2)

        if faultstring == '-':
            faultstring = l10n_pe_edi_get_error_by_code(faultcode)

        # If there is no faultcode, there is no error
        if not faultcode:
            return False, False, False

        res = (_('Error received from SUNAT'),
               _('Code: %s<br/>Message: %s') % (faultcode, faultstring))

        error_type = 'rejected'

        # check if faultcode is parseable to int, if doesn't it will be
        # considered as not sent
        error_code = False
        try:
            faultcode = int(faultcode)
        except ValueError:
            error_code = True

        # Error code between '0100' and '1999' is considered as not sent
        if error_code or 100 <= faultcode <= 1999:
            error_type = 'not_sent'

        # Error code >= 4000, SUNAT recognizes as VALID with Details
        elif faultcode >= 4000:
            error_type = 'warning'

        # If there is a error but was sent and is not a warning, was rejected
        return res + (error_type,)

    @api.multi
    def action_send_to_sunat(self):
        """Send to SUNAT the current document and register the response
        received from the sendBill service"""
        for document in self:
            attachment = document.l10n_pe_edi_retrieve_last_attachment()
            if not attachment:
                document.message_post(
                    subject=_('Error sending file'), message_type='comment',
                    body=_('There is no attachment generated'))
                continue

            res = document._l10n_pe_edi_prepare_and_send(
                service_name='send_bill', attachment=attachment)

            error_title, error_msg, error_type = (
                self.l10n_pe_edi_get_error(res))

            if error_msg:
                document.message_post(subject=error_title, body=error_msg,
                                      message_type='comment')

            if error_type == 'not_sent':
                continue

            app_response = res.xpath('//applicationResponse')
            cdr_encoded = app_response[0].text if app_response else ''

            code = False
            date = False
            if cdr_encoded:
                cdr = document.l10n_pe_edi_get_xml_etree(
                    ublpe=cdr_encoded, file_fmt="R-%(name)s.xml")
                base_path = '/ar:ApplicationResponse/cac:DocumentResponse'
                code_path = '%s//cbc:ResponseCode' % base_path
                code = document.l10n_pe_edi_xpath(cdr, code_path)
                code = code[0].text if code else False
                date = self.l10n_pe_edi_xpath(cdr, '//cbc:ResponseDate')
                date = date[0] if date else False

            # If the document is valid if gets code 0 or warning, in counter
            # case it was rejected by SUNAT
            status = 'with_error'
            if code == '0' or error_type == 'warning':
                status = 'valid'
            document.l10n_pe_edi_pse_status = status

            if status == 'with_error' and code:
                msg = '%s: %s %s' % (
                    _('Code:'), code, l10n_pe_edi_get_error_by_code(code))
                document.message_post(body=msg, message_type='comment')

            if not cdr_encoded or not date:
                continue
            document.l10n_pe_edi_cdr_date = date.text[:10]

            cdr_name = 'CDR-%s' % attachment.name
            document._l10n_pe_edi_sunat_save_cdr(filename=cdr_name,
                                                 content=cdr_encoded,
                                                 invoice_ids=document)

    l10n_pe_edi_amount_taxable = fields.Monetary(
        string="Taxable amount", copy=False, readonly=True, store=True,
        help="Represent the total amount that a tax is applied",
        compute="_compute_l10n_pe_edi_totals")
    l10n_pe_edi_amount_unaffected = fields.Monetary(
        string="Unaffected Amount", copy=False, readonly=True, store=True,
        help="Represent the total amount of unaffected lines with"
        " no tax set in the line", compute="_compute_l10n_pe_edi_totals")
    l10n_pe_edi_amount_exonerated = fields.Monetary(
        string="Exonerated Amount", copy=False, readonly=True, store=True,
        help="Represent the total amount of lines with tax equal "
        "to zero", compute="_compute_l10n_pe_edi_totals")
    l10n_pe_edi_amount_free = fields.Monetary(
        string="Total of free charge", copy=False, readonly=True, store=True,
        help="Represent the total amount of lines given for free,"
        " this amount is the sum of referential prices multiplied their qty.",
        compute="_compute_l10n_pe_edi_totals")
    l10n_pe_edi_total_discounts = fields.Monetary(
        string="Total discounts", copy=False, readonly=True,
        store=True, help="It represents the following computations:\n"
        "1. sum of line discounts, or\n2. sum of line discounts + overall "
        "discount", compute="_compute_l10n_pe_edi_totals")
    l10n_pe_edi_global_discounts = fields.Monetary(
        string="Global discounts", copy=False, readonly=True,
        store=True, help="It represents global discounts computes as negative "
        "priced lines", compute="_compute_l10n_pe_edi_totals")
    l10n_pe_edi_total_igv = fields.Monetary(
        string="Total IGV taxes", copy=False, readonly=True,
        store=True, help="It represent the total taxes amount for IGV taxes",
        compute="_compute_l10n_pe_edi_totals")
    l10n_pe_edi_total_isc = fields.Monetary(
        string="Total ISC taxes", copy=False, readonly=True,
        store=True, help="It represent the total taxes amount for ISC "
        "related taxes", compute="_compute_l10n_pe_edi_totals")
    l10n_pe_edi_total_otros = fields.Monetary(
        string="Total Others taxes", copy=False, readonly=True,
        store=True, help="It represent the total taxes amount for other taxes "
        "not considered in IGV and ISC", compute="_compute_l10n_pe_edi_totals")
    l10n_pe_edi_summary_id = fields.Many2one(
        'ir.attachment', string="Summary Document", readonly=True,
        copy=False, help="In case this invoice gets included in a summary "
        "document, this will contain the attachment")
    l10n_pe_edi_ticket_number = fields.Char(
        "Ticket Number", help="After the document have been sent to SUNAT, a "
        "ticket service number will be returned in order to ask for it later",
        readonly=True, copy=False)
    l10n_pe_edi_serie = fields.Char(
        size=4, store=True, compute="_compute_l10n_pe_edi_serie",
        help="Correspond to the journal prefix based on 4 alphanumeric "
        "digits beginning with a F letter.")
    l10n_pe_edi_correlative = fields.Char(
        size=8, store=True, compute="_compute_l10n_pe_edi_serie",
        help="Correspond to the incremental sequential value set once the "
        "invoice gets validated.")
    l10n_pe_edi_cdr_date = fields.Date(
        "Valid CDR date time", help="The date of the SUNATs response",
        copy=False,)
    l10n_pe_edi_error_message = fields.Char(
        "Error Message", help="If there is a not valid condition before "
        "the document gets validated, it will be contained",
        compute="_compute_l10n_pe_edi_error_message")

    @api.multi
    def _l10n_pe_edi_check_for_errors(self):
        self.ensure_one()
        error_log = []
        doc_type = self.l10n_pe_document_type
        vat_code = self.partner_id.l10n_pe_edi_vat_code
        # This keep documents from received a rejection from SUNAT with
        # error code 2016 that is when the following cases met:
        #  - Invoices issued with a VAT different than RUC (type=6)
        #  - Boletas issued with a VAT different than DNI (type=1) and
        #  False (for amounts LE S/ 700)
        if (doc_type == '01' and vat_code != '6' or
                doc_type == '03' and vat_code not in [False, '1']):
            error_log.append(
                _('If you want to issue an Invoice, please '
                  'indicate a partner with a RUC, in counter case if '
                  'you want to issue a Ticket please indicate a partner '
                  'with a DNI'))

        # In case the document is a Boleta de Venta and the amount total
        # gets greater than S/700, VAT number must be provided on customer
        # as Res. 1999-007 sect 3.10 dictates (https://goo.gl/zquB9T). In the
        # other hand when issuing a Factura de Venta the VAT needs to be set.
        if not self.partner_id.vat and (
                doc_type == '01' or
                doc_type == '03' and self.amount_total > 700):
            error_log.append(
                _('VAT cannot be empty, is required the customer '
                  'contains a valid VAT for the following cases: '
                  '1. Boleta with a total amount greater than S/ 700. '
                  '2. Invoice'))

        # -----------------------
        # Check the configuration
        # -----------------------
        # -Check certificate
        certificate_ids = self.company_id.l10n_pe_edi_certificate_ids
        certificate_id = certificate_ids.sudo().get_valid_certificate()
        if not certificate_id:
            error_log.append(_('No valid certificate found'))

        return error_log

    @api.multi
    @api.depends('partner_id.l10n_pe_edi_vat_code', 'l10n_pe_document_type')
    def _compute_l10n_pe_edi_error_message(self):
        """Compute error message (if any) based on known validations"""
        for invoice in self.filtered(lambda r: r.l10n_pe_edi_is_required() and
                                     r.partner_id):
            error_log = invoice._l10n_pe_edi_check_for_errors()
            invoice.l10n_pe_edi_error_message = '\n'.join(error_log)

    @api.multi
    @api.constrains('number', 'move_name')
    def _constraint_check_number(self):
        """Raise a validation error exception when the invoice number does not
        met format set by SUNAT
        """
        number_rgx = r"[FB]{1}[A-Z0-9]{3}-[0-9]{1,8}"
        rgx = re.compile(number_rgx)
        for invoice in self.filtered(lambda r: r.l10n_pe_edi_is_required() and
                                     r.state in ['open', 'paid']):
            number = invoice.number or invoice.move_name
            if not number and not rgx.match(number):
                raise ValidationError(_(
                    "Invoice number '%s' does not meet the format:\n"
                    " - Go to the journal sequence and set a prefix like: "
                    "'F**1-' or 'B**1-', including the '-' sign"
                ) % invoice.number)

    @api.multi
    @api.depends('number')
    def _compute_l10n_pe_edi_serie(self):
        """Serial of document, used for Voided documents xml documents
        """
        for invoice in self.filtered(lambda r: r.l10n_pe_edi_is_required()):
            number = invoice.number or invoice.move_name
            if not number or '-' not in number:
                continue
            number_split = number.split('-')
            invoice.update({
                'l10n_pe_edi_serie': number_split[0],
                'l10n_pe_edi_correlative': number_split[1]
            })

    @api.model
    def l10n_pe_edi_get_customer_dni(self):
        """In Peru if the VAT is not set for the customer, a generic DNI can be
        used: '00000000' within the electronic document
        :return: A ordered pair with DNI code based on SUNAT catalogs and
        the DNI if the customer have these values, in counter case
        a '1' and the generic DNI will be returned to be used.
        """
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id
        if not partner.vat:
            self.message_post(body=_('Using Generic DNI because no vat found'),
                              subtype='account.mt_invoice_validated',
                              message_type='comment')
            return ('1', '00000000')
        return (partner.l10n_pe_edi_vat_code, partner.l10n_pe_vat_number)

    @api.multi
    @api.depends('amount_tax', 'amount_untaxed')
    def _compute_l10n_pe_edi_totals(self):
        """Compute invoice totals amounts as:
            - Taxable to IGV amount
            - Unaffected to IGV amount
            - Exonerated to IGV amount
            - Given for free total amount
            - Discount total amount
        """
        for invoice in self.filtered(lambda r: r.l10n_pe_edi_is_required()):
            vals = {
                'taxable': 0,
                'unaffected': 0,
                'exonerated': 0,
                'free': 0,
                'discounts': 0,
            }
            empty = self.env['account.invoice.tax']
            taxes = defaultdict(lambda: self.env['account.invoice.tax'])
            for tax in invoice.tax_line_ids:
                taxes[tax.tax_id.tax_group_id.name] += tax

            # negative priced lines will be taken as discounts
            discount_lines = invoice.invoice_line_ids.filtered(
                lambda r: r.quantity and r.price_unit < 0)

            for line in invoice.invoice_line_ids - discount_lines:
                currency = line.invoice_id.currency_id
                price_unit = line.price_unit * (
                    1 - (line.discount or 0.0) / 100.0)
                taxes_list = line.invoice_line_tax_ids.compute_all(
                    price_unit, currency, line.quantity,
                    product=line.product_id,
                    partner=line.invoice_id.partner_id)

                if line.price_unit == 0:
                    vals['free'] = vals['free'] + \
                        line.l10n_pe_edi_ref_price * line.quantity
                    continue

                if not taxes_list['taxes']:
                    vals['unaffected'] = vals['unaffected'] +\
                        line.price_subtotal
                    continue

                if taxes_list['total_excluded'] == \
                        taxes_list['total_included']:
                    vals['exonerated'] = vals['exonerated'] + \
                        taxes_list['total_excluded']

                if taxes_list['total_excluded'] != \
                        taxes_list['total_included']:
                    vals['taxable'] = vals['taxable'] + \
                        taxes_list['total_excluded']

                if line.discount:
                    discount_amount = (line.price_unit *
                                       (line.discount * line.quantity) / 100.0)
                    vals['discounts'] = vals['discounts'] + discount_amount
            invoice.update({
                'l10n_pe_edi_amount_taxable': vals['taxable'],
                'l10n_pe_edi_amount_unaffected': vals['unaffected'],
                'l10n_pe_edi_amount_exonerated': vals['exonerated'],
                'l10n_pe_edi_amount_free': vals['free'],
                'l10n_pe_edi_total_discounts': vals['discounts'] +
                abs(sum(discount_lines.mapped('price_subtotal'))),
                'l10n_pe_edi_global_discounts':
                abs(sum(discount_lines.mapped('price_subtotal'))),
                'l10n_pe_edi_total_igv':
                sum(taxes.get('IGV', empty).mapped('amount')),
                'l10n_pe_edi_total_isc':
                sum(taxes.get('ISC', empty).mapped('amount')),
                'l10n_pe_edi_total_otros':
                sum(taxes.get('OTROS', empty).mapped('amount')),
            })

    @api.multi
    def l10n_pe_edi_action_send_summary_sunat(self):
        """Send to SUNAT the attachment and then keep the ticket number
        received if no error.
        """
        self.ensure_one()
        invoices = self.search([('l10n_pe_edi_summary_id', '=',
                                 self.l10n_pe_edi_summary_id.id)])
        attachment_x_inv = groupby(invoices,
                                   lambda r: r.l10n_pe_edi_summary_id)
        for attachment, records in attachment_x_inv:
            invoice_ids = self.browse([r.id for r in records])
            response = self._l10n_pe_edi_prepare_and_send(
                service_name='send_summary', attachment=attachment,
                company=attachment.company_id)

            error_title, error_msg, error_type = (
                self.l10n_pe_edi_get_error(response))
            if error_msg:
                for invoice in invoice_ids:
                    invoice.message_post(subject=error_title, body=error_msg,
                                         message_type='comment')

            if error_type == 'not_sent':
                continue

            if error_msg and error_type != 'warning':
                invoice_ids.write({'l10n_pe_edi_pse_status': 'with_error'})
                continue
            ticket_no = response.xpath('//ticket')
            ticket_no = ticket_no[0].text if ticket_no else False
            invoice_ids.write({'l10n_pe_edi_ticket_number': ticket_no})

    @api.multi
    def l10n_pe_edi_action_get_status_sunat(self):
        """Get status for a ticket related to the attachment
        document. A CDR zip file will be created if SUNAT processed the
        document (successfully or not). In counter case, the document may be
        still processing (code=98) and no action can be taken until it
        finished.
        """
        self.ensure_one()
        invoices = self.search([('l10n_pe_edi_summary_id', '=',
                                 self.l10n_pe_edi_summary_id.id)])
        attachment_x_inv = groupby(invoices,
                                   lambda r: r.l10n_pe_edi_summary_id)
        for attachment, records in attachment_x_inv:
            invoice_ids = self.browse([r.id for r in records])
            response = self._l10n_pe_edi_prepare_and_send(
                service_name='get_status',
                ticket_no=invoice_ids[0].l10n_pe_edi_ticket_number,
                company=attachment.company_id)

            error_title, error_msg, error_type = (
                self.l10n_pe_edi_get_error(response))
            for invoice in error_msg and invoice_ids or []:
                invoice.message_post(subject=error_title, body=error_msg,
                                     message_type='comment')

            # Local error ocurred
            if error_type == 'not_sent':
                continue

            status_code = response.xpath('//status/statusCode')

            # check if status code is parseable to int, if doesn't it will be
            # ignored
            status_code = self._process_statusCode(
                status_code, invoice_ids, attachment)
            if status_code is False:
                continue

            zip_name = attachment.name
            valid_invoices = invoice_ids.filtered(
                lambda r: r.state in ['open', 'paid', 'cancel'] and
                'RC' in zip_name or r.state == 'cancel' and 'RA' in zip_name)

            # Detect if there are documents that changed their odoo state after
            # were included in a summary and cannot be updated
            invalid_invoices = invoice_ids - valid_invoices

            # If there are cancelled boletas included in a ticket summary
            # should be ready to be included and notified to SUNAT
            invalid_invoices.filtered(lambda r: r.state == 'cancel').write({
                'l10n_pe_edi_pse_status': 'to_cancel',
                'l10n_pe_edi_ticket_number': False,
                'l10n_pe_edi_summary_id': False,
            })

            # if there is not invoices, the summary was already processed as
            # invalid one
            if not valid_invoices:
                continue

            # SUNAT status transition based on odoo state
            new_status = {
                'cancel': 'cancelled',
                'open': 'valid',
                'paid': 'valid',
            }
            for document in valid_invoices:
                status = new_status.get(document.state)
                if status_code != 0 or error_type == 'rejected':
                    status = 'with_error'
                document.l10n_pe_edi_pse_status = (
                    status if document.l10n_pe_edi_pse_status !=
                    'to_be_cancelled' else 'to_cancel')

            cdr_content = response.xpath('//status/content')
            cdr_content = cdr_content[0].text if cdr_content else False

            if not cdr_content:
                continue

            # Get CDR, and update values
            cdr = valid_invoices[0].l10n_pe_edi_get_xml_etree(
                ublpe=cdr_content, file_fmt="R-%(name)s.xml",
                file_name=attachment.name)

            cdr_attachment = self.env['ir.attachment']
            cdr_name = 'CDR-%s' % attachment.name
            try:
                # Validate is not a malformed zip file
                with tempfile.TemporaryFile() as zip_file:
                    zip_decoded = base64.b64decode(cdr_content)
                    zip_file.write(zip_decoded)
                    zipfile.ZipFile(zip_file, 'r')

                # Save SUNAT CDR into a new attachment
                cdr_attachment = self._l10n_pe_edi_sunat_save_cdr(
                    filename=cdr_name, content=cdr_content)
                message = _(
                    "A CDR have been received for %s") % attachment.name
            except zipfile.BadZipfile:
                message = _("SUNAT returned a corrupted CDR file")
                encoded = base64.b64encode(etree.tostring(response))
                cdr_attachment = self.env['ir.attachment'].create({
                    'datas': encoded,
                    'res_model': self._name,
                    'mimetype': 'application/zip',
                    'name': cdr_name,
                    'datas_fname': cdr_name,
                })
                status = 'with_error'
                continue
            finally:
                for invoice in valid_invoices:
                    invoice.message_post(message, message_type='comment',
                                         attachment_ids=cdr_attachment.ids)
                    if status == 'with_error':
                        invoice.l10n_pe_edi_pse_status = status
                        invoice.message_post('%s code: %s' % (_(
                            "Error received"), status_code))
            valid_invoices.filtered(
                lambda r: r.l10n_pe_edi_pse_status != 'with_error').write({
                    'l10n_pe_edi_ticket_number': False})
            valid_invoices -= valid_invoices.filtered(
                lambda r: r.l10n_pe_edi_pse_status == 'with_error')
            if valid_invoices:
                valid_invoices._l10n_pe_edi_update_cdr_date(cdr_name, cdr)

    @api.multi
    def _process_statusCode(self, status_code, invoice_ids, attachment):
        """If there is a coincidence in the fault list then we are stopping the
        process and writing a message for that document"""
        fault_error = ''
        try:
            fault_error = l10n_pe_edi_get_error_by_code(status_code[0].text)
            temp_code = int(status_code[0].text)
        except (ValueError, IndexError):
            message = '%s: %s' % (_("Sunat is returning something unexpected"),
                                  status_code[0].text)
            self._message_post(invoice_ids, message)
            return False

        # If document is still processing by SUNAT, do nothing but set
        # state and log in chatter
        if temp_code == 98:
            message = '%s %s' % (
                _('This document is still being processing by '
                  'SUNAT in the document %s'), attachment.name)
            self._message_post(invoice_ids, message, 'in_process')
            return False
        # Any error from the list shall be registered as a message
        if fault_error != 'Error code not recognized':
            message = '%s: %s' % (
                _("SUNAT is sending us this message"), fault_error)
            self._message_post(invoice_ids, message, 'with_error')
            return False
        return temp_code

    @api.multi
    def _message_post(self, invoice_ids, message, status=False):
        for invoice in invoice_ids:
            invoice.message_post(body=message, message_type='comment')
            if status:
                invoice.l10n_pe_edi_pse_status = status

    @api.multi
    def _l10n_pe_edi_update_cdr_date(self, cdr_name, cdr_xml):
        """Update document CDR date taken from cdr xml content
        :param cdr_name: CDR name to be processed
        :param cdr_xml: CDR content in xml tree form
        """
        date = self.l10n_pe_edi_xpath(cdr_xml, '//cbc:ResponseDate')
        try:
            date = date[0].text[:10] if date else False
            fields.Datetime.from_string(date)
            self.update({'l10n_pe_edi_cdr_date': date})
        except (ValueError, TypeError, IndexError):
            for invoice in self:
                invoice.message_post(
                    body=_("Wrong CDR Date format received in %s: '%s'") %
                    (cdr_name, date), message_type='comment')

    @api.multi
    def l10n_pe_edi_search_ra(self, vals):
        """Search cancelled invoices and tickets that at least are not included
        in a voided document. Take in count cancelled invoices notified as
        valid and cancelled tickets (wherever were notified or not) based on
        their issue date that are not cancelled.
        """
        invoices = self.search([
            ('type', 'in', ['out_refund', 'out_invoice']),
            ('date_invoice', '=', vals.get('reference_date')),
            ('state', '=', 'cancel'),
            ('l10n_pe_edi_summary_id', '=', False),
            ('l10n_pe_document_type', '=', '01')])

        invoices = invoices.filtered(
            lambda r: not r.l10n_pe_edi_ticket_number and
            (r.l10n_pe_document_type == '01' and
             r.l10n_pe_edi_pse_status == 'to_cancel'))
        return invoices

    @api.multi
    def l10n_pe_edi_get_ra_values(self):
        """Get the values for Voided Document. returns the values in a dict to
        be used when rendering the xml document
        :return: values in a dict will be returned
        """
        return {
            'company': self.mapped('company_id'),
            'reference_date': self.env.context.get('reference_date'),
            'issue_date': self.env.context.get('issue_date'),
            'number': self.env.context.get('number'),
            'records': self
        }

    @api.multi
    def l10n_pe_edi_generate_summary_ra(self):
        vals = self.l10n_pe_edi_get_ra_values()
        invoices = self.l10n_pe_edi_search_ra(vals)
        return invoices.l10n_pe_edi_generate_summary('ra')

    @api.multi
    def l10n_pe_edi_search_rc(self, vals):
        """Search and return records to be included in the next
        Ticket Summary document.
        :vals: values that contains at least the reference date for invoices
        :return: A record set of tickets
        """
        company = self.env.user.company_id
        # TODO: improve the way this search works
        all_tickets = self.search([
            ('type', 'in', ['out_refund', 'out_invoice']),
            ('date_invoice', '=', vals.get('reference_date')),
            ('company_id', '=', company.id),
            ('l10n_pe_document_type', 'in', ['03', '07', '08']),
            ('l10n_pe_edi_pse_status', 'not in', ['valid', 'cancelled',
                                                  'in_process']),
            ('amount_total', '>=', 0.0),
            ('l10n_pe_edi_amount_taxable', '>=', 0.0),
            ('l10n_pe_edi_ticket_number', '=', False),
        ])
        tickets = all_tickets.filtered(
            lambda r: r.l10n_pe_document_type == '03' or (
                r.l10n_pe_document_type in ['07', '08'] and
                r.refund_invoice_id.l10n_pe_document_type == '03'))
        tickets_related_filtered = self.l10n_pe_edi_related_documents(tickets)
        return tickets_related_filtered

    @api.multi
    def l10n_pe_edi_get_rc_values(self):
        """Get the values for Ticket Summary. Based on a record set of ticket
        invoices, get the required values to be used when rendering the
        ticket summary XML document.
        :return: values in a dict will be returned
        """

        res = []
        for record in self:
            vat_info = record.l10n_pe_edi_get_customer_dni()
            additional_info = record.l10n_pe_edi_get_additional_values()
            reference = (
                record.refund_invoice_id.number if
                record.l10n_pe_document_type in ['07', '08'] else False)
            res.append({
                'serie': record.l10n_pe_edi_serie,
                'doc_type': record.l10n_pe_document_type,
                'total_taxable': record.l10n_pe_edi_amount_taxable,
                'total_exonerated': record.l10n_pe_edi_amount_exonerated,
                'total_unaffected': record.l10n_pe_edi_amount_unaffected,
                'amount_total': record.amount_total,
                'currency': record.currency_id.name,
                'number': record.number or record.move_name,
                'vat_additional': vat_info[0],
                'vat_code': vat_info[1],
                'status': additional_info['status'],
                'typeCode': additional_info['typeCode'],
                'reference': reference,

                # DEAR ME: There are no other charges that applies at
                # this time the following dict entry is set to 0 on purpose
                # to be filled when needed
                'other_charges': 0,

                'taxes': [{
                    'edi_id': '1000',
                    'name': 'IGV',
                    'code': 'VAT',
                    'amount_tax': record.l10n_pe_edi_total_igv,
                }, {
                    'edi_id': '2000',
                    'name': 'ISC',
                    'code': 'EXC',
                    'amount_tax': record.l10n_pe_edi_total_isc,
                }, {
                    'edi_id': '9999',
                    'name': 'OTROS',
                    'code': 'OTH',
                    'amount_tax': record.l10n_pe_edi_total_otros,
                }],

            })
        return {
            'company': self.env.user.company_id,
            'reference_date': self.env.context.get('reference_date'),
            'issue_date': self.env.context.get('issue_date'),
            'number': self.env.context.get('number'),
            'records': res
        }

    @api.multi
    def l10n_pe_edi_generate_summary_rc(self):
        vals = self.l10n_pe_edi_get_rc_values()
        invoices = self.l10n_pe_edi_search_rc(vals)
        return invoices.l10n_pe_edi_generate_summary('rc')

    def l10n_pe_edi_generate_summary(self, summary_type):
        """Generate a summary document with the given invoice
        records and the parameters passed from context.
        :return: id of attachment created, in counter case a dictionary with
        error.
        """
        if not self:
            return {'error': _('There are no documents to be processed')}

        if not summary_type:
            return {'error': _('Summary type to be generated is not set')}

        values_func = 'l10n_pe_edi_get_%s_values' % summary_type
        attachment_ids = []
        comp_x_records = groupby(self, lambda r: r.company_id)
        summary_message = {'rc': 'Daily Summary', 'ra': 'Voided Summary'}
        for company_id, records in comp_x_records:
            invoice_ids = self.browse([r.id for r in records])
            values = getattr(invoice_ids, values_func)()
            version = self.l10n_pe_edi_get_pse_version()
            vals = get_xsd_template_names(summary_type.upper(), version)

            # Compute ublpe
            ublpe = self.env['ir.qweb'].render(vals[0],
                                               values=values)

            # Replace back colons in namespaces to have a valid UBLPE document
            ublpe = ublpe.replace('__', ':')

            # Include xml namespace to indicate xml's root element
            replace_dict = {'dn': vals[2]}
            ublpe = ublpe.replace(
                '<%(dn)s' % replace_dict,
                '<%(dn)s xmlns="urn:sunat:names:specification:ubl:peru:schema'
                ':xsd:%(dn)s-1"' % replace_dict)

            tree = fromstring(ublpe)

            xml_signed = self._l10n_pe_edi_sign_xml(tree, company_id)

            # Create ZIP file
            filename = ('%s-%s' % (company_id.partner_id.l10n_pe_vat_number,
                        values.get('number')))

            xml_str = etree.tostring(xml_signed, xml_declaration=True,
                                     encoding='ISO-8859-1')
            attachment = self.l10n_pe_edi_create_zipfile(filename, xml_str)
            invoice_ids.write({
                'l10n_pe_edi_summary_id': attachment.id,
                'l10n_pe_edi_ticket_number': False,
            })

            self.filtered(
                lambda r: r.l10n_pe_edi_pse_status != 'to_be_cancelled').write(
                    {'l10n_pe_edi_pse_status': 'in_process', })

            message = _("This invoice has been included in the %s: <a href=# "
                        "data-oe-model=ir.attachment data-oe-id=%d>%s</a>") % (
                            summary_message[summary_type],
                            attachment.id, attachment.datas_fname)
            for invoice in invoice_ids:
                invoice.message_post(message_type='comment', body=message)
                if invoice.l10n_pe_edi_pse_status == 'to_be_cancelled':
                    invoice.message_post(body=_('This document should run agai'
                                                'n the summary generation'),
                                         message_type='comment')
            attachment_ids.append(attachment.id)
        return {'attachment_ids': attachment_ids}

    def l10n_pe_edi_search_lt(self):
        reference_date = self.env.context.get('reference_date')
        company = self.env.user.company_id
        # TODO: improve the way this search works, because we don't how this
        # search will behave under big lots of documents
        invoices = self.search([
            ('type', 'in', ['out_refund', 'out_invoice']),
            ('date_invoice', '=', reference_date),
            ('company_id', '=', company.id),
            ('l10n_pe_document_type', 'in', ['01', '07', '08']),
            ('l10n_pe_edi_pse_status', '=', 'signed'),
            ('state', 'in', ['open', 'paid']),
            ('l10n_pe_edi_summary_id', '=', False),
        ])
        invoices = invoices.filtered(
            lambda r: r.l10n_pe_document_type == '01' or (
                r.l10n_pe_document_type in ['07', '08'] and
                r.refund_invoice_id.l10n_pe_document_type == '01'))
        return invoices

    def l10n_pe_edi_create_zipfile_multi(self, filename, xml_files):
        with osutil.tempdir() as temdir, tempfile.TemporaryFile() as t_zip:
            for xml_fname, content in xml_files.items():
                xml_file = join(temdir, xml_fname)
                with open(xml_file, "w") as res_file:
                    res_file.write(content)
            osutil.zip_dir(temdir, t_zip, include_dir=False)
            t_zip.seek(0)
            encoded = base64.b64encode(t_zip.read())
        attachment = self.env['ir.attachment'].create({
            'datas': encoded,
            'res_model': self._name,
            'mimetype': 'application/zip',
            'name': filename,
            'datas_fname': filename,
        })
        return attachment

    def l10n_pe_edi_generate_summary_lt(self):
        invoices = self.l10n_pe_edi_search_lt()
        if not invoices:
            return {'error': _('There are no documents to be processed')}

        comp_x_records = groupby(invoices, lambda r: r.company_id)
        attachments = self.env['ir.attachment'].browse()
        for company_id, records in comp_x_records:
            xml_x_company = {}
            invoice_ids = self.browse([r.id for r in records])
            for invoice in invoice_ids:
                attachment = invoice.l10n_pe_edi_retrieve_last_attachment()
                encoded_file = attachment.datas
                xml_doc = invoice.l10n_pe_edi_get_xml_etree(ublpe=encoded_file)
                xml_filename = "%s.xml" % splitext(attachment.datas_fname)[0]
                xml_x_company.update({xml_filename: etree.tostring(xml_doc)})

            attachment_name = ('%s-%s.zip' % (
                company_id.partner_id.l10n_pe_vat_number,
                self.env.context.get('number')))
            attachment = self.l10n_pe_edi_create_zipfile_multi(
                attachment_name, xml_x_company)

            message = _("This invoice has been included in")
            invoice_ids.write({
                'l10n_pe_edi_summary_id': attachment.id,
                'l10n_pe_edi_pse_status': 'in_process',
            })
            for invoice in invoice_ids:
                invoice.message_post(body=message, message_type='comment',
                                     attachment_ids=attachment.ids,)

                attachments |= attachment
        return {'attachment_ids': attachments.ids}

    @api.multi
    def l10n_pe_edi_cron_send_voided_documents(self, days):
        """This method runs the logic to report to the SUNAT the voided
        documents.
        :param int days: specifies the amount of days before the execution of
        this method, if 0 or greater than 7 this method will early return
            Invoices and tickets:
                They need to be previously sent and accepted by the SUNAT
                The date in count is one day after the document has been
                    accepted by the SUNAT
                Must have a cancel reason in l10n_pe_cancel_reason field
            Tickets that haven't been sent to the SUNAT
                The date is the creation of the ticket
            The day after: if you create a document the day 1 at 11:59 PM and
            you cancell it at day 2 at 00:00 AM you can send it on the lot of
            day 2.
        """

        if days > 7:
            _logger.info("Because of SUNAT standards we are taking 7 instead"
                         " of %s", days)
            days = 7
        today = self.env['l10n_pe_edi.certificate'].get_pe_current_datetime()
        limit_date = today - timedelta(days=days)
        limit_date_str = fields.datetime.strftime(
            limit_date, tools.DEFAULT_SERVER_DATE_FORMAT)
        today_str = fields.datetime.strftime(
            today, tools.DEFAULT_SERVER_DATE_FORMAT)
        invoices = self.search([
            ('type', 'in', ['out_refund', 'out_invoice']),
            ('state', '=', 'cancel'),
            ('l10n_pe_edi_summary_id', '=', False),
            ('l10n_pe_cancel_reason', '!=', False),
            ('l10n_pe_document_type', '=', '01'),
            ('l10n_pe_edi_ticket_number', '=', False),
            ('date_invoice', '>=', limit_date_str),
            ('date_invoice', '<', today_str),
        ])
        invoices = invoices.filtered(lambda r: (
            r.l10n_pe_edi_pse_status == 'to_cancel' and
            r.l10n_pe_edi_cdr_date >= limit_date_str))
        vals = {'reference_date': '',
                'summary_type': '',
                'number': '',
                'issue_date': ''}
        group_by_date = groupby(invoices,
                                lambda r: r.date_invoice)
        for date, records in group_by_date:
            invoices_ids = self.browse([r.id for r in records])
            wizard = self.env['l10n_pe_edi.summary.wizard'].create({
                'reference_date': date, 'summary_type': 'ra'})
            vals.update({'reference_date': date,
                         'summary_type': wizard.summary_type,
                         'number': wizard.number,
                         'issue_date': wizard.issue_date})

            invoices_ids.with_context(vals).l10n_pe_edi_generate_summary('ra')
            if invoices_ids:
                invoices_ids[0].l10n_pe_edi_action_send_summary_sunat()

    @api.multi
    def l10n_pe_edi_cron_send_valid_documents(self, days=7, doc_type='all'):
        """This method runs the logic to send documents each time is executed
            The rules on this method are based on https://goo.gl/c5SX8M
            Documents with a 7 days tops are going to be sent to the SUNAT:
                - Invoices and related documents individually
                - Tickets
            Relative documents of tickets are going to be sent once their
            origin document is valid.
        """

        today = self.env['l10n_pe_edi.certificate'].get_pe_current_datetime()
        limit_date = today - timedelta(days=days)
        limit_date_str = fields.datetime.strftime(
            limit_date, tools.DEFAULT_SERVER_DATE_FORMAT)
        document_types = {
            'all': ['01', '03', '07', '08'],
            'tickets': ['03', '07', '08'],
            'invoices': ['01', '07', '08'],
            'second_wave': ['03', '07', '08']}

        document_type = document_types[doc_type]
        all_documents = self.search([
            ('type', 'in', ['out_refund', 'out_invoice']),
            ('date_invoice', '>=', limit_date_str),
            ('l10n_pe_edi_pse_status', 'in',
             ['signed', 'to_be_cancelled', 'to_cancel', 'in_process']),
            ('l10n_pe_edi_ticket_number', '=', False),
            ('l10n_pe_document_type', 'in', document_type)])

        vals = {'reference_date': '',
                'summary_type': '',
                'number': '',
                'issue_date': ''}

        all_invoices = all_documents.filtered(
            lambda r: r.l10n_pe_document_type == '01' or (
                r.l10n_pe_document_type in ['07', '08'] and
                r.refund_invoice_id.l10n_pe_document_type == '01'))

        invoices = self.l10n_pe_edi_related_documents(all_invoices)
        invoices.action_send_to_sunat()

        # DEAR DEV: please note that this is just not the right answer, we need
        # a better way to deal with the error at the moment to send an invoice
        invoices.filtered(
            lambda r: r.l10n_pe_edi_pse_status == 'signed'
        ).l10n_pe_edi_action_get_status_cdr_sunat()

        all_tickets = all_documents.filtered(
            lambda r: (r.l10n_pe_document_type == '03' or
                       (r.l10n_pe_document_type in ['07', '08'] and
                        r.refund_invoice_id.l10n_pe_document_type == '03')) and
            (r.l10n_pe_edi_pse_status in ['signed', 'in_process',
                                          'to_cancel']) and
            (r.amount_total >= 0.0 and
             r.l10n_pe_edi_amount_taxable >= 0.0))
        tickets = self.l10n_pe_edi_related_documents(all_tickets)

        # Send documents that were meant to be sent
        tickets -= self._process_previous_summaries(tickets)
        if doc_type == 'second_wave':
            tickets = tickets.filtered(
                lambda r: (r.state == 'cancel' and
                           r.l10n_pe_document_type == '03') or
                r.l10n_pe_document_type in ['07', '08'])
        if not tickets:
            return False

        group_by_date = groupby(
            tickets, lambda r:
            [r.date_invoice, r.l10n_pe_edi_summary_id])

        for values, records in group_by_date:
            tickets_ids = self.browse([r.id for r in records])
            wizard = self.env['l10n_pe_edi.summary.wizard'].create({
                'reference_date': values[0], 'summary_type': 'rc'})

            vals.update({'reference_date': values[0],
                         'summary_type': wizard.summary_type,
                         'number': wizard.number,
                         'issue_date': wizard.issue_date})
            tickets_ids.with_context(vals).l10n_pe_edi_generate_summary('rc')
            if tickets_ids:
                tickets_ids[0].l10n_pe_edi_action_send_summary_sunat()

    @api.multi
    def l10n_pe_edi_cron_get_status_documents(self):
        """This method call getStatus method on documents pending to received
        SUNAT status. These documents needs to be in process state and a
        Summary and a ticket number related to them.
        """

        invoices = self.search([
            ('type', 'in', ['out_refund', 'out_invoice']),
            ('state', 'in', ['open', 'paid', 'cancel']),
            ('l10n_pe_edi_ticket_number', '!=', False),
            ('l10n_pe_edi_pse_status', 'in',
             ['in_process', 'to_be_cancelled']),
            ('l10n_pe_edi_summary_id', '!=', False),
        ])

        group_by_ticket = groupby(invoices,
                                  lambda r: r.l10n_pe_edi_ticket_number)

        for ticket_number, records in group_by_ticket:
            invoice_ids = self.browse([r.id for r in records])

            # if for some reason there is no invoices for the ticket number
            # we need to avoid IndexError here.
            if not invoice_ids:
                continue

            _logger.info("Getting status for ticket %s", ticket_number)
            invoice_ids[0].l10n_pe_edi_action_get_status_sunat()

    def action_invoice_draft(self):
        """The document will be letting pass to draft when the following use
        cases are not met:
            - Invoices/Boletas validated in SUNAT contains a CDR-ACCEPTED date
            - Boletas in process to be notified are associated with a summary
            - Invoices/Boletas cancelled already have a ticket number
        """
        not_allow = self.env['account.invoice']
        if (not self.env.user.has_group(
           'l10n_pe_edi.res_group_super_user_manager')):

            not_allow = self.filtered(
                lambda r: r.l10n_pe_edi_is_required() and
                (r.l10n_pe_edi_cdr_date or r.l10n_pe_edi_summary_id or
                    r.l10n_pe_edi_ticket_number or
                 r.l10n_pe_edi_pse_status in ['with_error', 'to_cancel']))

            for invoice in not_allow:
                invoice.message_post(
                    subject=_('An error occurred while setting to draft.'),
                    message_type='comment',
                    body=_('This invoice have been notified at least once, '
                           'SUNAT does not supports re-validation or re-cancel'
                           'lation after it have been validated/cancelled'))
        return super(AccountInvoice, self - not_allow).action_invoice_draft()

    @api.multi
    def l10n_pe_edi_action_regenerate(self):
        self.ensure_one()
        old_summary = self.l10n_pe_edi_summary_id
        # Search invoices related
        invoices = self.search([
            ('l10n_pe_edi_summary_id', '=', old_summary.id)])

        summary_name, _file_ext = splitext(old_summary.name)
        try:
            company_vat, doc_type, issue_date, _file_index = (
                summary_name.split('-'))
        except ValueError:
            for invoice in invoices:
                invoice.message_post(body=_("Summary document %s cannot be "
                                            "regenerated") % old_summary.name,
                                     message_type='comment')
            return

        summary_type = doc_type.lower()

        # Search for new correlative
        summary_like_name = "%s-%s-%s%%.zip" % (company_vat, doc_type,
                                                issue_date)
        attachment_name = self.env['ir.attachment'].search(
            [('name', '=ilike', summary_like_name)], order="id desc", limit=1
        ).mapped('name')
        correlative = 1
        try:
            correlative = int(splitext(attachment_name[0])[0].split('-')[-1])
        except (IndexError, ValueError):
            for invoice in invoices:
                invoice.message_post(body=_("Summary document %s cannot be "
                                            "regenerated") % old_summary.name,
                                     message_type='comment')
            return

        # Get data for regenerate
        vals = {
            'issue_date': datetime.strptime(issue_date, '%Y%m%d').strftime(
                '%Y-%m-%d'),
            'reference_date': invoices[0].date_invoice,
            'summary_type': doc_type.lower(),
            'number': '%s-%s-%s' % (doc_type, issue_date, str(correlative + 1))
        }

        # Regenerate summary
        res = invoices.with_context(vals).l10n_pe_edi_generate_summary(
            summary_type)

        attachment_ids = res.get('attachment_ids')
        new_summary = self.env['ir.attachment'].browse(attachment_ids)
        for invoice in invoices:
            invoice.message_post(subject="Document regenerated",
                                 body="Document %s have been regenerated into "
                                 "%s" % (old_summary.name, new_summary.name),
                                 attachment_ids=attachment_ids,
                                 message_type='comment')

    def l10n_pe_edi_get_barcode(self):
        """Creating a barcode image for the printed representation
        Currently supports PDF417
        More information about SUNAT and barcodes in https://goo.gl/68DBjV
        """
        document = self.l10n_pe_edi_get_xml_etree()
        if document is False:
            return
        codes = ''
        values = [
            self.company_id.partner_id.l10n_pe_vat_number,
            self.l10n_pe_document_type,
            self.l10n_pe_edi_serie,
            self.l10n_pe_edi_correlative,
            str(self.l10n_pe_edi_total_igv),
            str(self.amount_total),
            self.date_invoice,
            self.l10n_pe_edi_xpath(document, ('//cac:AccountingCustomerParty/'
                                   'cbc:AdditionalAccountID'))[0].text,
            self.partner_id.l10n_pe_vat_number or '',
            self.l10n_pe_edi_xpath(document, '//ds:DigestValue')[0].text,
            self.l10n_pe_edi_xpath(document, '//ds:SignatureValue')[0].text,
            '']
        codes = '|'.join(values)
        with osutil.tempdir() as tempdir:
            codes = encode(codes, columns=8)
            image_data = render_image(codes, scale=5)
            image_file_path = join(tempdir, "%s.png" % self.number)
            image_data.save(image_file_path)
            with open(image_file_path, "rb") as image_data:
                _bytes = image_data.read()
                encoded = base64.b64encode(_bytes)
        return encoded

    @api.multi
    def l10n_pe_edi_get_additional_values(self):
        self.ensure_one()
        values = {'status': False, 'typeCode': False}

        if not self.l10n_pe_edi_cdr_date:
            values = {'status': 1, 'typeCode': '03'}
            if self.state == 'cancel':
                self.l10n_pe_edi_pse_status = 'to_be_cancelled'

        else:
            if (self.l10n_pe_edi_pse_status
                in ['in_process', 'to_cancel', 'with_error'] and
                self.state == 'cancel'):
                values = {'status': 3, 'typeCode': '03'}
        return values

    @api.multi
    def l10n_pe_edi_related_documents(self, documents):
        """This method will return the documents that it's related document is
        valid or if they aren't l10n_pe_document_type 07 or 08
        """
        debit_credit_notes = documents.filtered(
            lambda r: r.l10n_pe_document_type in ['07', '08'])
        for debit_credit_note in debit_credit_notes:
            invoice_origin = debit_credit_note.refund_invoice_id
            if (invoice_origin and
               invoice_origin.l10n_pe_edi_pse_status != 'valid'):
                documents -= debit_credit_note
        return documents

    @api.multi
    def action_invoice_open(self):
        invoices_not_to_open = self.filtered(
            lambda r: r.l10n_pe_edi_is_required and (
                r.amount_total < 0 or (
                    r.l10n_pe_edi_amount_free == 0.0 and
                    not sum(r.invoice_line_ids.mapped('price_unit')))))
        for invoice in invoices_not_to_open:
            message = _(
                "SUNAT does not support 0.0 as sum of all price_units, "
                "one or more products should have a list price higher that 0")
            if invoice.amount_total < 0:
                message = "SUNAT does not support negative as totals"
            invoice.message_post(
                body=_("The current document can't be validated because: %s "
                       % message))
        return super(AccountInvoice,
                     self - invoices_not_to_open).action_invoice_open()

    @api.multi
    def _process_previous_summaries(self, documents):
        """All the summaries that were having problems and aren't processed
        with errors will be send again in the next execution.
        """
        documents = documents.filtered(
            lambda r: r.l10n_pe_edi_summary_id and
            r.l10n_pe_edi_pse_status in
            ['to_be_cancelled', 'in_process', 'to_cancel'] and
            r.l10n_pe_edi_summary_id and not r.l10n_pe_edi_cdr_date)
        group_by_date = groupby(documents, lambda r: r.l10n_pe_edi_summary_id)

        for _attachment, records in group_by_date:
            tickets_ids = self.browse([r.id for r in records])
            if tickets_ids:
                tickets_ids[0].l10n_pe_edi_action_send_summary_sunat()
            documents -= tickets_ids
        return documents
