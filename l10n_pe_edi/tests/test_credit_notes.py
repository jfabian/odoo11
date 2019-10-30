# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from .test_common import TestCommon


class TestCreditNotes(TestCommon):

    def test_01_xml_creation_for_credit_note(self):
        """Generate a credit note from an invoice, and validate the XML
        attachment gets generated.
        Validate also the refund reason is being written after the credit
        note is created from wizard
        """
        invoice = self.create_invoice()
        vals = invoice.invoice_print()
        report_file = vals.get('report_file', '')
        content = self.get_report_content(invoice, report_file)
        title = self.get_text(content, "//div[@id='doc_title']")
        self.assertIn('ELECTRONIC INVOICE', title,
                      'Electronic invoice expected')
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
        vals = refund_id.invoice_print()
        report_file = vals.get('report_file', '')
        content_refund = self.get_report_content(refund_id, report_file)
        title_refund = self.get_text(content_refund, "//div[@id='doc_title']")
        self.assertIn('ELECTRONIC CREDIT NOTE', title_refund,
                      'Refund invoice expected')
        self.assertEquals(refund_id.l10n_pe_refund_reason, '03',
                          "Expected reason for the credit note: 03")
        zip_name = '%(name)s' % ({'name': refund_id.l10n_pe_edi_ublpe_name})
        attachment = refund_id.message_ids.mapped('attachment_ids').filtered(
            lambda r: r.datas_fname == zip_name)
        self.assertTrue(attachment,
                        'Credit note attachment with the xml generated is '
                        'missing.')
