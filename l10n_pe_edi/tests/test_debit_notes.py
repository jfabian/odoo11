# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from .test_common import TestCommon


class TestDebitNotes(TestCommon):

    def test_01_xml_creation_for_debit_note(self):
        """Validate that basic debit note xml can be rendered
        """
        invoice = self.create_invoice()
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
        vals = debit_id.invoice_print()
        report_file = vals.get('report_file', '')
        content_charge = self.get_report_content(debit_id, report_file)
        title_charge = self.get_text(content_charge, "//div[@id='doc_title']")
        self.assertIn('ELECTRONIC DEBIT NOTE', title_charge,
                      'Charge invoice expected')
        self.assertEquals(debit_id.l10n_pe_charge_reason, '02',
                          "Expected reason for the debit note: 02")
        zip_name = '%(name)s' % ({'name': debit_id.l10n_pe_edi_ublpe_name})
        attachment = debit_id.message_ids.mapped('attachment_ids').filtered(
            lambda r: r.datas_fname == zip_name)
        self.assertTrue(attachment,
                        'Debit note attachment with the xml generated is '
                        'missing.')
