# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from .test_common import TestCommon


class TestInvoicePrint(TestCommon):

    def test_01_test_boleta_print(self):
        """Ticket 1 with 1 to test the printed representation."""

        ticket = self.create_invoice(
            partner=self.env.ref('base.res_partner_12'),
            journal_id=self.env.ref('l10n_pe_edi.journal_ebol'))
        vals = ticket.invoice_print()
        report_file = vals.get('report_file', '')
        content_ticket = self.get_report_content(ticket, report_file)
        title_ticket = self.get_text(content_ticket, "//div[@id='doc_title']")
        self.assertIn('ELECTRONIC TICKET', title_ticket,
                      'Electronic ticket expected')
