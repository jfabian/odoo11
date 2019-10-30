# -*- coding: utf-8 -*-
import logging
from odoo import SUPERUSER_ID, api
_logger = logging.getLogger(__name__)


def set_boletas_original_state(cr):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        _logger.info('Setting l10n_pe_edi_cdr_date for invoices')
        invoices = env['account.invoice'].search(
            [('l10n_pe_edi_cdr_date', '=', None),
             ('l10n_pe_edi_pse_status', '=', 'with_error'),
             ('l10n_pe_document_type', '=', '03')]
        ).filtered(
            lambda r: r.l10n_pe_edi_is_required() and
            u'<p>El ticket no existe</p>' in r.message_ids.mapped('body'))
        invoices.update({'l10n_pe_edi_pse_status': 'signed'})


def migrate(cr, version):
    if not version:
        return
    set_boletas_original_state(cr)
