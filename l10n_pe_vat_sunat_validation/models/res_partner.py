# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
"""File to inherit res_partnet to get name & address to partner with your RUC
"""
import json
from urllib import urlencode

import requests

from odoo import _, api, models


class ResPartner(models.Model):
    """Inherit res.partner to get your name & address from the xml returned by
    SUNAT
    """
    _inherit = 'res.partner'

    @api.onchange('vat')
    def onchange_vat(self):
        """Update name & address partner by SUNAT
        """
        if not self.vat or self.country_id != self.env.ref('base.pe'):
            return
        self.vat = self.vat.upper()
        self.check_vat()
        param = self.env['ir.config_parameter']
        params = {
            'token': param.get_param('sunatdb.api_token', '').strip(),
        }
        api_url = param.get_param('sunatdb.api_url', '').strip()
        if not (all(params.values()) and api_url):
            return
        params.update({
            'rfc': self.l10n_pe_vat_number
        })
        try:
            base_url = '%(url)s/rfc?%(params)s' % {
                'url': api_url,
                'params': urlencode(params)}
            client = requests.get(base_url)
            result = client.ok and json.loads(client.text) or {
                'error_message': True}
        except BaseException, e:
            result = {'error_message': e}
        if result.get('error_message'):
            return {
                'warning': {
                    'title': _('Client not found'),
                    'message': _('It is posible that it persist because:'
                                 '\n\n* A connection problem with the '
                                 'SUNAT server\n* The data is incorrect'
                                 '\n\nPlease verify the data and try '
                                 'again, otherwise proceed to fill the '
                                 'data manually')}}
        result.pop('vat', 'No')
        district_code = 'PE%(city)s' % result
        district_obj = self.env['res.country.district']
        district_brw = district_obj.search([('code', '=', district_code)],
                                           limit=1)
        result.update({
            'l10n_pe_district_id': district_brw.id,
            'zip': (district_brw.code or '')[2:],
            })
        self.update(result)
