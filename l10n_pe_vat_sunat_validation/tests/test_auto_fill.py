# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import json
from urllib import urlencode

import requests_mock

from odoo.tests import common


class TestSunatResponses(common.TransactionCase):

    def setUp(self):
        super(TestSunatResponses, self).setUp()

        self.partner = self.env.ref('base.partner_root')

    @requests_mock.mock()
    def test_auto_fill(self, requests):

        parameter_obj = self.env['ir.config_parameter']
        district = self.env.ref('l10n_pe_toponyms.PE080105')
        api_token = parameter_obj.get_param('sunatdb.api_token', '').strip()
        api_url = parameter_obj.get_param('sunatdb.api_url', '').strip()
        vat = 'R10076413989'
        params = {
            'token': api_token,
            'rfc': vat[1:]
        }
        base_url = '%s/rfc?%s' % (api_url, urlencode(params))
        requests.get(base_url,
                     text=json.dumps({'name': 'Vx', 'street': 'Vx Street',
                                      'city': '080105'}))

        # Set Vat
        self.partner.country_id = self.env.ref('base.pe')
        self.partner.vat = 'PE' + vat

        self.partner.onchange_vat()
        self.partner.onchange_l10n_pe_district_id()

        # Check Street
        self.assertEquals(self.partner.street,
                          'Vx Street',
                          'The street is not the same returned by the api')

        # Check district
        self.assertEquals(self.partner.l10n_pe_district_id.id,
                          district.id,
                          'The street is not the same returned by the api')

        # Check province
        self.assertEquals(self.partner.l10n_pe_province_id.id,
                          district.province_id.id,
                          'The street is not the same returned by the api')

        # Check state
        self.assertEquals(self.partner.state_id.id,
                          district.province_id.state_id.id,
                          'The street is not the same returned by the api')

        # Check name
        self.assertEquals(self.partner.name,
                          'Vx',
                          'The name is not the same returned by the api')

    @requests_mock.mock()
    def test_no_response(self, requests):

        parameter_obj = self.env['ir.config_parameter']
        api_token = parameter_obj.get_param('sunatdb.api_token', '').strip()
        api_url = parameter_obj.get_param('sunatdb.api_url', '').strip()
        vat = '10076413989'
        params = {
            'token': api_token,
            'rfc': vat[1:]
        }
        base_url = '%s/rfc?%s' % (api_url, urlencode(params))
        requests.get(base_url,
                     text=json.dumps({'error_message':
                                      'Partner with vat %s not found' %
                                      vat}))
        # Set Vat
        self.partner.country_id = self.env.ref('base.pe')
        self.partner.vat = 'PER' + vat
        result = self.partner.onchange_vat()

        # Check result
        self.assertTrue(isinstance(result, dict),
                        'Expected to find a dictionary.')
        self.assertIn('warning', result, 'Expected to find a warning dict.')
        self.assertIn('message', result.get('warning'),
                      'Expected to find a warning message.')

    @requests_mock.mock()
    def test_no_city(self, requests):

        parameter_obj = self.env['ir.config_parameter']
        api_token = parameter_obj.get_param('sunatdb.api_token', '').strip()
        api_url = parameter_obj.get_param('sunatdb.api_url', '').strip()
        vat = 'R10076413989'
        params = {
            'token': api_token,
            'rfc': vat[1:]
        }
        base_url = '%s/rfc?%s' % (api_url, urlencode(params))
        requests.get(base_url,
                     text=json.dumps({'name': 'Vx', 'street': False,
                                      'city': False}))
        # Set Vat
        self.partner.country_id = self.env.ref('base.pe')
        self.partner.vat = 'PE' + vat
        self.partner.onchange_vat()
        self.partner.onchange_l10n_pe_district_id()
        # Check state
        self.assertEquals(self.partner.state_id.id,
                          False,
                          'Expected to receive False as state_id value')
        # Check zip
        self.assertEquals(self.partner.zip,
                          '',
                          'Expected to receive a void string as zip value')
        # Check city
        self.assertEquals(self.partner.city,
                          False,
                          'Expected to receive a False as city value')
