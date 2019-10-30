# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import tools

from .test_common import TestCommon


class TestOtherJournalCode(TestCommon):

    @tools.mute_logger('pysimplesoap.helpers')
    def test_01_send_to_sunat_wrong_prefix(self):
        """Change the prefix of the journal, sent it to the SUNAT and check
        that the errors have been reported in the chatter
        """

        journal_id = self.create_journal('test', 'FAC')
        journal_id.sequence_id.prefix = 'FAX-'
        invoice = self.create_invoice(journal_id=journal_id)
        invoice.action_send_to_sunat()
        messages = invoice.message_ids
        expected = ("El nombre del archivo ZIP es incorrecto")
        message = messages.filtered(lambda r: expected in r.body)
        self.assertIn(expected, message.body)
