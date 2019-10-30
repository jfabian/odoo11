# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests import common


class TestCommon(common.TransactionCase):

    def setUp(self):
        super(TestCommon, self).setUp()
        self.journal_sale = self.env['account.journal'].search(
            [('type', '=', 'sale')], limit=1)
        self.journal_purchase = self.env['account.journal'].search(
            [('type', '=', 'purchase')], limit=1)
        self.uid = self.env['res.users'].with_context(
            {'no_reset_password': True}
        ).create({
            'name': 'User billing pe',
            'login': 'pe_billing_user',
            'email': 'pe_billing_user@demo.com',
            'company_id': self.env.ref('base.main_company').id,
            'groups_id': [(6, 0, [self.ref('account.group_account_invoice')])]
        })
        self.report_common = self.env['account.report.context.common']

    def create_invoice(self, invoice_amount=700, journal_id=False,
                       tax_ids=False, partner=None, date=None):
        if partner is None:
            partner = self.env.ref('base.res_partner_2')
        product = self.env.ref('product.product_product_5')

        invoice = self.env['account.invoice'].with_env(
            self.env(user=self.uid)).create({
                'partner_id': partner.id,
                'type': 'out_invoice',
                'journal_id': (journal_id or self.journal_sale).id,
                'invoice_line_ids': [
                    (0, 0, {
                        'product_id': product.id,
                        'uom_id': product.uom_id.id,
                        'quantity': 1,
                        'price_unit': invoice_amount,
                        'name': 'new line #1',
                        'account_id': self.env.ref('l10n_pe.70111_01').id,
                        'invoice_line_tax_ids': tax_ids and [(6, 0, tax_ids)],
                    })
                ],
            })
        invoice.action_invoice_open()
        return invoice

    def create_journal(self, name="Factura", code="FAC", jtype='sale'):
        return self.env['account.journal'].create({
            'company_id': self.env.ref('base.main_company').id,
            'name': name,
            'code': code,
            'type': jtype,
            'update_posted': True
        })
