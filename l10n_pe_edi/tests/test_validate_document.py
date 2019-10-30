# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo.exceptions import UserError

from .test_common import TestCommon


class TestValidateDocument(TestCommon):
    def test_01_validate_a_ticket(self):
        """Creating a ticket with a partner without DNI will raise a user error
        """
        with self.assertRaises(UserError):
            self.create_invoice(journal_id=self.journal_bol)

    def test_02_validate_an_invoice(self):
        """Creating an invoice with a partner without RUC will raise an
        user error"""
        with self.assertRaises(UserError):
            self.create_invoice(partner=self.env.ref('base.res_partner_12'),
                                journal_id=self.journal_id)
