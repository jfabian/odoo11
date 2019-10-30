# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import time

from .test_common import TestCommon


class TestSupplierInvoiceCreation(TestCommon):

    def test_01_supplier_invoice_creation(self):
        """Supplier invoices cannot be affected by xml generation and
        validation process, this test will create a supplier invoice
        and get it validated to the final stage
        """
        company = self.env.ref('base.main_company')
        serv_cost = self.env.ref('product.service_cost_01')
        account_receivable = self.env['account.account'].create({
            'code': 'XXXX1',
            'name': 'Sale - Test Payable Account',
            'user_type_id':
            self.env.ref('account.data_account_type_receivable').id,
            'reconcile': True
        })
        account_outcome = self.env['account.account'].create({
            'code': 'XYYY1',
            'name': 'Purchase - Test Account',
            'user_type_id':
            self.env.ref('account.data_account_type_direct_costs').id
        })
        invoice = self.env['account.invoice'].create({
            'partner_id': self.env.ref('base.res_partner_1').id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y-%m')+'-15',
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Product 1',
                    'product_id': serv_cost.id,
                    'quantity': 3,
                    'uom_id': serv_cost.uom_id.id,
                    'price_unit': 7.0,
                    'account_id': account_outcome.id
                }),
                (0, 0, {
                    'name': 'Product 2',
                    'product_id': serv_cost.id,
                    'quantity': 7,
                    'uom_id': serv_cost.uom_id.id,
                    'price_unit': 25.0,
                    'account_id': account_outcome.id
                }),
            ],
            'account_id': account_receivable.id,
            'currency_id': company.currency_id.id,
        })
        self.assertEqual(invoice.type, 'in_invoice',
                         'Expected a Supplier Invoice')
        invoice.invoice_validate()
        self.assertFalse(invoice.l10n_pe_edi_ublpe_name,
                         'This field represents xml file name and cannot be '
                         'filled when a supplier invoice is validated')
        self.assertEqual(invoice.state, 'paid')
