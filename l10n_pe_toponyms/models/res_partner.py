# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _get_default_country_id(self):
        return self.env.ref('base.pe')

    l10n_pe_province_id = fields.Many2one(
        'res.country.province', 'Province',
        domain="[('state_id.country_id', '=', country_id)]")
    l10n_pe_district_id = fields.Many2one(
        'res.country.district', 'District',
        domain="[('province_id.state_id.country_id', '=', country_id)]")
    country_id = fields.Many2one(
        default=_get_default_country_id)
    state_id = fields.Many2one(
        domain="[('country_id', '=', country_id)]")

    @api.onchange('l10n_pe_district_id')
    def onchange_l10n_pe_district_id(self):
        """Fill the fields l10n_pe_province_id and state_id with the
        corresponding information extracted from the field l10n_pe_district_id
        """
        self.update({
            'l10n_pe_province_id': self.l10n_pe_district_id.province_id.id,
            'state_id': self.l10n_pe_district_id.province_id.state_id.id,
        })


class ResCountryProvince(models.Model):
    _name = 'res.country.province'

    name = fields.Char(required=True, index=True)
    code = fields.Char(required=True, index=True)
    district_ids = fields.One2many(
        'res.country.district', 'province_id', 'Districts')
    state_id = fields.Many2one(
        'res.country.state', 'State', index=True, required=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', _(
            'The code of the province must be unique !'))
    ]


class ResCountryDistrict(models.Model):
    _name = 'res.country.district'

    name = fields.Char(required=True, index=True)
    code = fields.Char(required=True, index=True)
    province_id = fields.Many2one(
        'res.country.province', 'Province', required=True, index=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', _(
            'The code of the district must be unique !'))
    ]
