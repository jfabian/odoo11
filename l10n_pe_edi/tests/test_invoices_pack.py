# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from .test_common import TestCommon


class TestInvoicesPack(TestCommon):

    def create_invoices(self):
        invoices = self.env['account.invoice']
        invoice = self.create_invoice()
        invoices += invoice
        invoice = self.create_invoice()
        invoices += invoice

        # create debit note for 1st invoice
        wizard = self.env['account.invoice.refund'].with_context({
            'active_ids': invoices[0].ids,
        }).create({
            'description': 'Debit note from unit test',
            'filter_refund': 'charge',
            'l10n_pe_charge_reason': '02',
        })
        wizard.invoice_refund()

        # create credit note for 2nd invoice
        wizard = self.env['account.invoice.refund'].with_context({
            'active_ids': invoices[1].ids,
        }).create({
            'description': 'Credit note from unit test',
            'filter_refund': 'refund',
            'l10n_pe_refund_reason': '04',
        })
        wizard.invoice_refund()
        notes = self.env['account.invoice'].search(
            [('refund_invoice_id', 'in', invoices.ids)])
        notes.action_invoice_open()
        invoices += notes
        return invoices

    def test_01_test_four_docs(self):
        today = self.env['l10n_pe_edi.certificate'].get_pe_current_datetime()
        date_invoice = today.date().strftime('%Y-%m-%d')
        self.create_invoices()
        wizard_obj = self.env['l10n_pe_edi.summary.wizard']
        wizard = wizard_obj.create({'reference_date': date_invoice,
                                    'summary_type': 'lt'})
        attachment_id = wizard.generate_document()
        attachment = self.env['ir.attachment'].browse(attachment_id)
        attachment_name = attachment.datas_fname

        statuses = self.env['account.invoice'].search(
            [('l10n_pe_edi_summary_id', 'in', attachment_id)]
        ).mapped('l10n_pe_edi_pse_status')

        self.assertEqual(set(statuses), set(['in_process']),
                         'Wrong status set for current invoices included '
                         'in %s' % attachment_name)

        self.assertIn('20565520572', attachment_name)
        self.assertIn('LT', attachment_name)
        self.assertIn('zip', attachment_name)
