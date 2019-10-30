# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    l10n_pe_vat_number = fields.Char(compute="_compute_vat_number")
    l10n_pe_edi_vat_code = fields.Selection(
        [
            ('0', 'Documento Tributario No Domiciliado Sin RUC'),
            ('1', 'Documento Nacional de Identidad'),
            ('4', 'Carnet de Extranjería'),
            ('6', 'Registro Único de Contribuyentes'),
            ('7', 'Pasaporte'),
            ('A', 'Cédula Diplomática de Identidad'),
        ], compute="_compute_vat_number", store=True)
    l10n_pe_edi_vat_type = fields.Selection(
        [
            ('D', 'Documento Nacional de Identidad'),
            ('R', 'Registro Único de Contribuyentes'),
        ], compute="_compute_vat_number", store=True)

    @api.model
    def explode_vat(self):
        if not self.vat:
            return (False, False)

        vat = self.vat[2:].replace(' ', '')

        if self.country_id == self.env.ref('base.pe'):
            return (vat[0], vat[1:])

        if self.country_id != self.env.ref('base.pe'):
            return (False, vat)

    @api.multi
    @api.depends('vat', 'commercial_partner_id')
    def _compute_vat_number(self):
        """Based on current vat validation and implementation, the following
        logic set the code associated and its vat without prefix
        chat on its vat field.
          0 - Documento Tributario No Domiciliado Sin RUC
        * 1 - Documento Nacional de Identidad
          4 - Carnet de Extranjería
        * 6 - Registro Único de Contribuyentes
          7 - Pasaporte
          A - Cédula Diplomática de Identidad

        this represent the catalog no. 6 of SUNAT (https://goo.gl/rGedAU) and
        (*) types included are supported in the core https://goo.gl/VInziW
        """
        for partner in self.filtered(lambda r: r.vat):
            vat_code = {'R': '6', 'D': '1'}
            vat_type, vat_number = partner.explode_vat()
            partner.l10n_pe_edi_vat_type = vat_type
            partner.l10n_pe_edi_vat_code = vat_code.get(vat_type)
            partner.l10n_pe_vat_number = vat_number
