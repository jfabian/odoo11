# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import tools

from .test_common import TestCommon


class TestSummaryGenerationRules(TestCommon):

    @tools.mute_logger('pysimplesoap.helpers')
    def test_01_debit_credit_summary_cron(self):
        invoice_today = self.create_invoice(journal_id=self.journal_id)
        ticket_today = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.journal_bol)

        credit_invoice_today = self.create_credit(invoice_today)
        debit_invoice_today = self.create_debit(invoice_today)

        credit_ticket_today = self.create_credit(ticket_today)
        debit_ticket_today = self.create_debit(ticket_today)

        self.account_invoice.l10n_pe_edi_cron_send_valid_documents()

        # No summary or valid to documents that at this point
        self.assertEqual(credit_invoice_today.l10n_pe_edi_pse_status, 'signed')
        self.assertEqual(debit_invoice_today.l10n_pe_edi_pse_status, 'signed')
        self.assertFalse(credit_ticket_today.l10n_pe_edi_summary_id)
        self.assertFalse(debit_ticket_today.l10n_pe_edi_summary_id)

        self.account_invoice.l10n_pe_edi_cron_get_status_documents()

        self.assertEqual(invoice_today.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_today.l10n_pe_edi_pse_status, 'valid')

        self.account_invoice.l10n_pe_edi_cron_send_valid_documents()

        # All deb/cred should be in_process or valid
        self.assertEqual(credit_invoice_today.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(debit_invoice_today.l10n_pe_edi_pse_status, 'valid')
        self.assertTrue(credit_ticket_today.l10n_pe_edi_summary_id)
        self.assertTrue(debit_ticket_today.l10n_pe_edi_summary_id)

    @tools.mute_logger('pysimplesoap.helpers')
    def test_02_debit_credit_summary_manual(self):
        invoice_today = self.create_invoice(journal_id=self.journal_id)
        ticket_today = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.journal_bol)

        credit_invoice_today = self.create_credit(invoice_today)
        debit_invoice_today = self.create_debit(invoice_today)

        credit_ticket_today = self.create_credit(ticket_today)
        debit_ticket_today = self.create_debit(ticket_today)

        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        wizard = wizard_obj.create({'reference_date': self.today_date,
                                    'summary_type': 'rc'})
        wizard.generate_document()
        ticket_today.l10n_pe_edi_action_send_summary_sunat()
        invoice_today.action_send_to_sunat()
        self.assertEqual(invoice_today.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(ticket_today.l10n_pe_edi_pse_status, 'in_process')
        ticket_today.l10n_pe_edi_action_get_status_sunat()
        self.assertEqual(ticket_today.l10n_pe_edi_pse_status, 'valid')

        # No summary or valid to documents that at this point for deb/cred
        self.assertEqual(credit_invoice_today.l10n_pe_edi_pse_status, 'signed')
        self.assertEqual(debit_invoice_today.l10n_pe_edi_pse_status, 'signed')
        self.assertFalse(credit_ticket_today.l10n_pe_edi_summary_id)
        self.assertFalse(debit_ticket_today.l10n_pe_edi_summary_id)

        # Summary for cred/deb
        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        wizard = wizard_obj.create({'reference_date': self.today_date,
                                    'summary_type': 'rc'})
        wizard.generate_document()
        self.assertTrue(credit_ticket_today.l10n_pe_edi_summary_id)
        self.assertTrue(debit_ticket_today.l10n_pe_edi_summary_id)

        # Send documents/summary to SUNAT
        credit_ticket_today.l10n_pe_edi_action_send_summary_sunat()
        credit_invoice_today.action_send_to_sunat()
        debit_invoice_today.action_send_to_sunat()

        self.assertEqual(credit_ticket_today.l10n_pe_edi_pse_status,
                         'in_process')
        self.assertEqual(debit_ticket_today.l10n_pe_edi_pse_status,
                         'in_process')
        debit_ticket_today.l10n_pe_edi_action_get_status_sunat()

        # All deb/cred should be in_process or valid
        self.assertEqual(credit_invoice_today.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(debit_invoice_today.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(credit_ticket_today.l10n_pe_edi_pse_status, 'valid')
        self.assertEqual(debit_ticket_today.l10n_pe_edi_pse_status, 'valid')
