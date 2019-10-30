# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from .test_common import TestCommon


class AccountPurchases(TestCommon):

    def setUp(self):
        super(AccountPurchases, self).setUp()
        self.report_model = 'l10n_pe.account.purchases.report'

    def test_01_get_ple_xml(self):
        context_data = self.report_common.return_context(self.report_model, {})
        self.create_invoice(journal_id=self.journal_purchase)
        data = self.env[context_data[0]].browse(context_data[1]).get_xml()
        self.assertTrue(data)

    def test_02_get_attributes_context(self):
        context_data = self.report_common.return_context(self.report_model, {})
        obj_context = self.env[context_data[0]].browse(context_data[1])

        self.assertTrue(
            obj_context.get_available_journal_ids_names_and_codes())
        self.assertTrue(obj_context.get_columns_names())
        self.assertEqual(obj_context.get_columns_names(),
                         [u'Date', u'Acc. Name/Number', u'Debit', u'Credit'])
        self.assertEqual(obj_context.get_columns_types(),
                         ['date', 'text', 'number', 'number'])
        self.assertTrue(obj_context.get_html_and_data())

    def test_03_attributes_report(self):
        report_obj = self.env['l10n_pe.account.purchases.report']
        self.assertIn('080100', report_obj.get_name())
        self.assertIn('080200', report_obj.with_context({
            'report_id': '2'}).get_name())
        self.assertEqual('PLE Purchases Report', report_obj.get_title())
        xml_report = self.env['account.financial.html.report.xml.export']
        self.assertTrue(xml_report.is_txt_export_available(report_obj))
        self.assertFalse(xml_report.is_txt_export_available(
            self.env['report.account.report_generalledger']))
        self.assertTrue(xml_report.check(
            'l10n_pe.account.general.ledger.report'))

    def test_04_report_context_common(self):
        context_obj = self.env['account.report.context.common']
        self.assertIn('l10n_pe.account.purchases.report',
                      context_obj._report_name_to_report_model().values())
