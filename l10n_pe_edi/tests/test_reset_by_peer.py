# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import socket

from mock import patch
import pysimplesoap

from odoo import tools

from .test_common import TestCommon


class SideEffect(object):

    def __init__(self, **kwargs):
        raise socket.error(104, 'Connection reset by peer')


class TestResetByPeer(TestCommon):

    @tools.mute_logger('pysimplesoap.helpers')
    def test_01_catch_errno_104(self):
        """Send an invoice to the SUNAT while mocking a Errno[104]
        """
        invoice = self.create_invoice()
        with patch.object(pysimplesoap.client.SoapClient, '__init__',
                          new=SideEffect):
            invoice.action_send_to_sunat()
        error_message = invoice.message_ids.filtered(lambda r: '[Errno 104]'
                                                     in r.body)
        expected_message = 'Conection reset by peer'
        self.assertEqual(error_message.subject, expected_message)
