# -*- coding: utf-8 -*-
import logging
from odoo import SUPERUSER_ID, api
_logger = logging.getLogger(__name__)


def set_l10n_pe_edi_cdr_date(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _logger.info('Setting l10n_pe_edi_cdr_date for invoices')
        invoices = env['account.invoice'].search(
            [('l10n_pe_edi_cdr_date', '=', None),
             ('l10n_pe_edi_pse_status', 'in', ['valid', 'to_cancel']),
             ('state', 'in', ['open', 'paid', 'cancelled']),
             ('l10n_pe_document_type', '=', '01'),
             ('l10n_pe_edi_cdr_date', '=', False)]
        ).filtered(lambda r: r.l10n_pe_edi_is_required())

        # update cdr_date for invoices
        for invoice in invoices:
            cdr_name = "CDR-%s" % invoice.l10n_pe_edi_ublpe_name
            attachment = env['ir.attachment'].search([('name', '=', cdr_name)])

            if not attachment:
                continue

            cdr = invoice.l10n_pe_edi_get_xml_etree(ublpe=attachment.datas,
                                                    file_fmt="R-%s.xml")
            date = env['account.invoice'].l10n_pe_edi_xpath(
                cdr, '//cbc:ResponseDate')

            invoice.l10n_pe_edi_cdr_date = date[0].text if date else False


def migrate(cr, version):
    if not version:
        return
    set_l10n_pe_edi_cdr_date(cr)
