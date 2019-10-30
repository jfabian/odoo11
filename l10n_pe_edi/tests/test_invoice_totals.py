# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from .test_common import TestCommon


class TestInvoiceTotals(TestCommon):

    def setUp(self):
        super(TestInvoiceTotals, self).setUp()
        self.account_receivable = self.env['account.account'].create({
            'code': 'XXXX1',
            'name': 'Sale - Test Payable Account',
            'user_type_id':
            self.env.ref('account.data_account_type_receivable').id,
            'reconcile': True
        })
        self.account_revenue = self.env['account.account'].search([
            ('user_type_id', '=', self.env.ref(
                'account.data_account_type_revenue').id)], limit=1)
        self.product1 = self.env.ref('product.product_product_1')
        self.product2 = self.env.ref('product.product_product_4')
        self.product3 = self.env.ref('product.product_product_22')
        self.product4 = self.env.ref('product.consu_delivery_02')
        self.tax_igv_id = self.env['account.tax'].search(
            [('name', '=', 'IGV 18% Venta'),
             ('amount', '=', 18.0)])
        self.tax_igv_id.write({
            'tax_group_id': self.env.ref('l10n_pe_edi.tax_group_igv').id})
        self.tax_exonerated_id = self.env['account.tax'].create({
            'name': 'Exonerado 0% Venta',
            'amount': 0,
            'amount_type': 'percent',
            'price_include': False,
            'type_tax_use': 'sale',
            'sequence': 50,
        })

    def test_01_test_invoice_totals(self):
        """Invoice 1 with 4 products, each with different taxes
        to test the totals in the invoice."""

        invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'type': 'out_invoice',
            'account_id': self.account_receivable.id,
            'invoice_line_ids': [
                (0, 0, {
                    'name': self.product1.name,
                    'product_id': self.product1.id,
                    'quantity': 50,
                    'uom_id': self.product1.uom_id.id,
                    'price_unit': 1.0,
                    'account_id': self.account_revenue.id,
                    'invoice_line_tax_ids': [(6, 0, self.tax_igv_id.ids)],
                    'discount': 10.0,
                }),
                (0, 0, {
                    'name': self.product2.name,
                    'product_id': self.product2.id,
                    'quantity': 50,
                    'uom_id': self.product2.uom_id.id,
                    'price_unit': 0,
                    'account_id': self.account_revenue.id,
                    'discount': 10.0,
                }),
                (0, 0, {
                    'name': self.product3.name,
                    'product_id': self.product3.id,
                    'quantity': 1,
                    'uom_id': self.product3.uom_id.id,
                    'price_unit': 3100.0,
                    'account_id': self.account_revenue.id,
                    'discount': 10.0,
                }),
                (0, 0, {
                    'name': self.product4.name,
                    'product_id': self.product4.id,
                    'quantity': 1,
                    'uom_id': self.product4.uom_id.id,
                    'price_unit': 40000.0,
                    'account_id': self.account_revenue.id,
                    'invoice_line_tax_ids': [
                        (6, 0, self.tax_exonerated_id.ids)],
                    'discount': 10.0,
                }),
            ],
        })
        self.assertEquals(invoice.l10n_pe_edi_amount_taxable, 45.0,
                          'Expected total for taxable amount: 45.0')
        self.assertEquals(invoice.l10n_pe_edi_amount_unaffected, 2790.0,
                          'Expected total for unaffected amount: 2790.0')
        self.assertEquals(invoice.l10n_pe_edi_amount_exonerated, 36000.0,
                          'Expected total exonerated amount: 36000.0')
        self.assertEquals(invoice.l10n_pe_edi_amount_free, 37500.0,
                          'Expected total free amount: 37500.0')
        self.assertEquals(invoice.l10n_pe_edi_total_discounts, 4005.0,
                          'Expected total discount amount: 4005.0')

    def test_02_included_in_price_taxable(self):
        """When having a IGV tax (with tax included in price )set in line
        with qty 1 and amount of 100.0, the invoice taxable amount must be
        84.75"""
        # Set include in price in tax
        self.tax_igv_id.write({'price_include': True})
        vals = [
            {'price_unit': 100.0,
             'invoice_line_tax_ids': self.tax_igv_id.ids},
        ]
        invoice = self.create_invoice_different_lines(
            partner=self.partner_bol, journal_id=self.journal_bol, lines=vals)
        self.assertEqual(invoice.l10n_pe_edi_amount_taxable,
                         84.75, 'Taxable amount is not 84.75')

    def test_03_use_multiple_taxes_same_group(self):
        """Test multiple same-group taxes in the same invoice when computing
        totals. As case of use this test includes a IGV 18% and IGV 7% each one
        in invoice line.
        """
        # Set copy tax to emulate two IGV taxes on invoice
        second_tax_id = self.tax_igv_id.copy()
        second_tax_id.amount = 7.0
        vals = [
            {'price_unit': 100.0,
             'invoice_line_tax_ids': self.tax_igv_id.ids},
            {'price_unit': 250.0,
             'invoice_line_tax_ids': second_tax_id.ids}
        ]
        invoice = self.create_invoice_different_lines(
            partner=self.partner_bol, journal_id=self.journal_bol, lines=vals)
        invoice.action_invoice_open()
        self.assertEqual(invoice.l10n_pe_edi_total_igv, 35.5,
                         'Total IGV must be 35.5=18.0(18%) + 17.5(7%)')

    def test_04_test_invoice_totals(self):
        """Invoice 1 with 2 products, one with a positive value and other with
        a negative value, the one with the negative value should be taken as a
        discount."""

        vals = [
            {'price_unit': 50,
             'invoice_line_tax_ids': self.tax_igv_id.ids},
            {'price_unit': -50,
             'invoice_line_tax_ids': self.tax_igv_id.ids}
        ]

        invoice = self.create_invoice_different_lines(
            partner=self.partner_bol, journal_id=self.journal_bol, lines=vals)
        invoice.action_invoice_open()
        self.assertEqual(invoice.amount_total, 0.0)
        self.assertEqual(invoice.l10n_pe_edi_total_discounts, 50.0)
