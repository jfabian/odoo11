# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from .test_common import TestCommon


class TestIGVAffectation(TestCommon):

    def test_01_xml_creation_for_credit_note(self):

        tax_igv_id = self.env['account.tax'].search(
            [('name', '=', 'IGV 18% Venta'),
             ('amount', '=', 18.0)])
        tax_exonerated_id = self.env['account.tax'].search(
            [('name', '=', 'Exonerado 0% Venta'), ('amount', '=', 0)])
        # Case 30
        # a default item is included in the invoice template.
        invoice0 = self.create_invoice()
        # Case 31
        invoice1 = self.create_invoice(invoice_amount=0)
        # Case 10
        invoice2 = self.create_invoice(tax_ids=tax_igv_id.ids)
        # Case 11
        invoice3 = self.create_invoice(
            invoice_amount=0,
            tax_ids=tax_igv_id.ids)
        # Case 20
        invoice4 = self.create_invoice(tax_ids=tax_exonerated_id.ids)
        # Case 21
        invoice5 = self.create_invoice(
            invoice_amount=0,
            tax_ids=tax_exonerated_id.ids)

        def case_val(line):
            cases = {
                '30': not line.invoice_line_tax_ids and line.price_unit,
                '31': not line.invoice_line_tax_ids and not line.price_unit,
                '20': line.invoice_line_tax_ids and line.price_unit and
                not sum(line.invoice_line_tax_ids.mapped('amount')),
                '21': line.invoice_line_tax_ids and not line.price_unit and
                not sum(line.invoice_line_tax_ids.mapped('amount')),
                '10': line.price_unit and
                sum(line.invoice_line_tax_ids.mapped('amount')),
                '11': not line.price_unit and
                sum(line.invoice_line_tax_ids.mapped('amount')),
                }
            val = cases[line.l10n_pe_exemption_reason]
            return val

        for line in invoice0.invoice_line_ids:
            self.assertTrue(case_val(line),
                            'Expected match with exemption reason 30')
        for line in invoice1.invoice_line_ids:
            self.assertTrue(case_val(line),
                            'Expected match with exemption reason 31')
        for line in invoice2.invoice_line_ids:
            self.assertTrue(case_val(line),
                            'Expected match with exemption reason 10')
        for line in invoice3.invoice_line_ids:
            self.assertTrue(case_val(line),
                            'Expected match with exemption reason 11')
        for line in invoice4.invoice_line_ids:
            self.assertTrue(case_val(line),
                            'Expected match with exemption reason 20')
        for line in invoice5.invoice_line_ids:
            self.assertTrue(case_val(line),
                            'Expected match with exemption reason 21')
