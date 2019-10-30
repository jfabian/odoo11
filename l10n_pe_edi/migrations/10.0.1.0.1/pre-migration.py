# -*- coding: utf-8 -*-
import logging
from odoo import api
_logger = logging.getLogger(__name__)


def set_enable_noupdate_for_crons(cr):
    with api.Environment.manage():
        _logger.info('Setting noupdate="1" for ir.crons of l10n_pe_edi')

        cr.execute("""UPDATE ir_model_data
                   SET noupdate='t'
                   WHERE module='l10n_pe_edi' AND model='ir.cron' AND
                   name IN %s""", (('ir_cron_send_voided_documents',
                                    'ir_cron_send_valid_documents',
                                    'ir_cron_get_status_documents'),))


def migrate(cr, version):
    if not version:
        return
    set_enable_noupdate_for_crons(cr)
