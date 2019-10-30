# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from .test_common import TestCommon


class TestSunatCatalogs(TestCommon):

    def test_01_amount_in_words(self):
        invoice = self.create_invoice(invoice_amount=2340.44)
        amount_words = invoice.get_additional_property('1000')
        self.assertIn("DOS MIL TRESCIENTOS CUARENTA CON 44/100",
                      amount_words)

        invoice = self.create_invoice(invoice_amount=579123.29)
        amount_words = invoice.get_additional_property('1000')
        self.assertIn('QUINIENTOS SETENTA Y NUEVE MIL CIENTO VEINTITR',
                      amount_words)
        self.assertIn('S CON 29/100', amount_words)

    def test_02_customer_factura_doc_type(self):
        invoice = self.create_invoice(journal_id=self.journal_id)
        vals = invoice.l10n_pe_document_type
        self.assertEqual(vals, '01',
                         "Invoice document with the journal 'FAC' type have "
                         "to be 01 for SUNAT")

    def test_03_customer_boleta_doc_type(self):
        invoice = self.create_invoice(partner=self.partner_bol,
                                      journal_id=self.journal_bol)
        vals = invoice.l10n_pe_document_type
        self.assertEqual(vals, '03',
                         "Invoice document with the journal 'BOL' type have "
                         "to be 03 for SUNAT")

    def test_04_customer_guia_de_remision_doc_type(self):

        journal_id = self.create_journal('Guia de Remisión', 'GR')
        invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_2').id,
            'journal_id': journal_id.id,
        })
        vals = invoice.l10n_pe_document_type
        self.assertEqual(vals, '09',
                         "Invoice document with the journal 'GR' type have "
                         "to be 09 for SUNAT")

    def test_05_validate_unece_product_uom(self):
        invoice = self.create_invoice()
        uom_id = invoice.invoice_line_ids.uom_id
        self.assertEqual(uom_id.l10n_pe_unece_code, 'C62',
                         "UoM unit must be represented by C62 code")

    def test_06_validate_price_code(self):
        invoice = self.create_invoice(invoice_amount=50)
        line = invoice.invoice_line_ids
        self.assertEqual(line.price_unit, 50,
                         'Price Unit expected to be 50, no free')
        self.assertEqual(line.l10n_pe_edi_ref_price, 0,
                         "Referential price should be zero")
        line.write({'price_unit': 0})
        line._compute_ref_price()
        self.assertEqual(line.price_unit, 0,
                         'Price Unit expected to be 0, as free invoice line')
        self.assertEqual(line.l10n_pe_edi_ref_price, 147.0,
                         "Referential price should be zero")

    def test_07_tax_exemption_reason_code(self):
        tax_id = self.env['account.tax'].search(
            [('name', '=', 'IGV 18% Venta'), ('amount', '=', 18.0)])
        invoice = self.create_invoice(tax_ids=tax_id.ids)
        line = invoice.invoice_line_ids[0]
        self.assertEqual(line.l10n_pe_exemption_reason, '10',
                         "The only reason code to be taken in count is: "
                         "10 with a 9.0 as tax amount")

    def test_08_tax_type_code(self):
        tax_id = self.env['account.tax'].search(
            [('name', '=', 'IGV 18% Venta'), ('amount', '=', 18.0)])
        invoice = self.create_invoice(tax_ids=tax_id.ids)
        tax = invoice.invoice_line_ids.invoice_line_tax_ids
        self.assertEqual(tax.l10n_pe_tax_type_code, '1000',
                         "The only tax_type_code_to be taken is: 1000 for VAT")

    def test_09_customer_credit_note(self):
        invoice = self.create_invoice()
        wizard = self.env['account.invoice.refund'].with_context({
            'active_ids': invoice.ids,
        }).create({
            'description': 'Refund from unit test',
            'filter_refund': 'refund'
        })

        wizard.invoice_refund()
        refund = self.env['account.invoice'].search(
            [('origin', '=', invoice.number)])
        vals = refund.l10n_pe_document_type
        self.assertEqual(vals, '07',
                         "A credit note is represented by a 07 for SUNAT")

    def test_10_validate_amount_types(self):
        invoice = self.create_invoice()
        amount_values = invoice.l10n_pe_amount_value_type
        self.assertEqual(amount_values, '01',
                         "amount type code unit code needs to be 01 "
                         "as the only one used")

    def test_11_additional_monetary_total_values(self):
        invoice = self.create_invoice(1500.00)
        vals = invoice.l10n_pe_monetary_total
        self.assertEqual(vals, '1001',
                         'The only monetary values expected is the total '
                         'taxable amount for the invoice with 1500.00')
