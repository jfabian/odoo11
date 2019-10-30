# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.depends(
        'partner_id.l10n_pe_province_id', 'partner_id.l10n_pe_district_id')
    def _compute_address_data(self):
        """ Read the 'address' functional fields. """
        for company in self:
            address = company.partner_id
            company.l10n_pe_province_id = address.l10n_pe_province_id
            company.l10n_pe_district_id = address.l10n_pe_district_id

    @api.multi
    def _inverse_address_data(self):
        """ Write the 'address' functional fields. """
        for company in self:
            address_data = company.partner_id.address_get(['default'])
            address = address_data.get('default')
            if address is not None:
                company.partner_id.write({
                    'l10n_pe_province_id': company.l10n_pe_province_id.id,
                    'l10n_pe_district_id': company.l10n_pe_district_id.id,
                })

    l10n_pe_province_id = fields.Many2one(
        'res.country.province', 'Province',
        compute=_compute_address_data,
        inverse=_inverse_address_data, multi='address',
        help='Province address for partner',
        domain="[('state_id', '=', state_id)]")
    l10n_pe_district_id = fields.Many2one(
        'res.country.district', 'District',
        compute=_compute_address_data,
        inverse=_inverse_address_data, multi='address',
        help='District address for partner',
        domain="[('province_id', '=', l10n_pe_province_id)]")
