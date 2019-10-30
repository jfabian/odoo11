# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from __future__ import division

from odoo import api, fields, models, tools


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    l10n_pe_exemption_reason = fields.Selection(
        [
            ('10', 'Gravado- Operación Onerosa'),
            ('11', 'Gravado- Retiro por premio'),
            ('12', 'Gravado- Retiro por donación'),
            ('13', 'Gravado- Retiro'),
            ('14', 'Gravado- Retiro por publicidad'),
            ('15', 'Gravado- Bonificaciones'),
            ('16', 'Gravado- Retiro por entrega a trabajadores'),
            ('17', 'Gravado- IVAP'),
            ('20', 'Exonerado- Operación Onerosa'),
            ('21', 'Exonerado- Transferencia Gratuita'),
            ('30', 'Inafecto- Operación Onerosa'),
            ('31', 'Inafecto- Retiro por Bonificación'),
            ('32', 'Inafecto- Retiro'),
            ('33', 'Inafecto- Retiro por Muestras Médicas'),
            ('34', 'Inafecto- Retiro por Convenio Colectivo'),
            ('35', 'Inafecto- Retiro por premio'),
            ('36', 'Inafecto- Retiro por publicidad'),
            ('40', 'Exportación')],
        help=u"Tipo de Afectación al IGV",
        compute="_compute_exemption_reason")

    @api.multi
    @api.depends('invoice_line_tax_ids', 'price_unit')
    def _compute_exemption_reason(self):
        """Indicates how the IGV affects the invoice line product
          * 10 'Gravado - Operación Onerosa'
          * 11 'Gravado - Retiro por premio'
            12 'Gravado - Retiro por donación'
            13 'Gravado - Retiro'
            14 'Gravado - Retiro por publicidad'
            15 'Gravado - Bonificaciones'
            16 'Gravado - Retiro por entrega a trabajadores'
            17 'Gravado - IVAP'
          * 20 'Exonerado - Operación Onerosa'
          * 21 'Exonerado - Transferencia Gratuita'
          * 30 'Inafecto - Operación Onerosa'
          * 31 'Inafecto - Retiro por Bonificación'
            32 'Inafecto - Retiro'
            33 'Inafecto - Retiro por Muestras Médicas'
            34 'Inafecto - Retiro por Convenio Colectivo'
            35 'Inafecto - Retiro por premio'
            36 'Inafecto - Retiro por publicidad'
            40 'Exportación'
        it represents the catalog no 7 of SUNAT.
        NOTE: Not all the cases are supported
        """
        # Inafecto
        self.filtered(lambda r: not r.invoice_line_tax_ids and r.price_unit).\
            update({'l10n_pe_exemption_reason': '30'})
        self.filtered(lambda r: not r.invoice_line_tax_ids and not r.price_unit
                      ).update({'l10n_pe_exemption_reason': '31'})

        # Exanerado
        self.filtered(lambda r: r.invoice_line_tax_ids and r.price_unit and
                      not sum(r.invoice_line_tax_ids.mapped('amount'))
                      ).update({'l10n_pe_exemption_reason': '20'})
        self.filtered(lambda r: r.invoice_line_tax_ids and not r.price_unit and
                      not sum(r.invoice_line_tax_ids.mapped('amount'))
                      ).update({'l10n_pe_exemption_reason': '21'})

        # Gravado
        self.filtered(lambda r: r.price_unit and
                      sum(r.invoice_line_tax_ids.mapped('amount'))).\
            update({'l10n_pe_exemption_reason': '10'})
        self.filtered(lambda r: not r.price_unit and
                      sum(r.invoice_line_tax_ids.mapped('amount'))).\
            update({'l10n_pe_exemption_reason': '11'})

    l10n_pe_edi_ref_price = fields.Monetary(string="Referential Price",
                                            copy=False, readonly=True,
                                            compute="_compute_ref_price",)

    @api.multi
    @api.depends('price_unit', 'invoice_id.date_invoice')
    def _compute_ref_price(self):
        for line in self.filtered(lambda r: not r.price_unit):
            line.l10n_pe_edi_ref_price = line.product_id.list_price

    @api.multi
    def _compute_subtotal_by_unit(self):
        """It returns the amount after discounts and taxes have been applied
        by item. Required for https://goo.gl/mjM7BJ, pt 15 page 36-37
        """
        for line in self:
            line.l10n_pe_subtotal_by_unit = (
                line.price_subtotal / line.quantity) if line.quantity else 0
            line.l10n_pe_edi_amount_taxed = line.mapped(
                lambda r: r.price_subtotal + (r.price_subtotal * sum(
                    [s.amount for s in r.invoice_line_tax_ids])/100.0))[0]

    l10n_pe_subtotal_by_unit = fields.Float(
        compute="_compute_subtotal_by_unit")
    l10n_pe_edi_amount_taxed = fields.Float(
        compute="_compute_subtotal_by_unit")

    @api.multi
    def l10n_pe_edi_discount_amt(self):
        """It computes the discount amount.
        """
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Account')
        return tools.float_round(self.price_unit * (self.discount / 100.0),
                                 precision) if self.discount else 0

    @api.multi
    def l10n_pe_edi_compute_taxes_values(self):
        """Returns all required values for cbc:TaxTotal details detailed in
        the section B.2.3. Tag TaxTotal in https://goo.gl/eh2ZyT
        This is taking only IGV in the values.
        """
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Account')
        # / ! \ Note: Dear future me. I am assuming one tax per group
        tax_igv = self.invoice_line_tax_ids.filtered(
            lambda r: r.tax_group_id.name == 'IGV')
        tax_isc = self.invoice_line_tax_ids.filtered(
            lambda r: r.tax_group_id.name == 'ISC')
        tax_otros = self.invoice_line_tax_ids.filtered(
            lambda r: r.tax_group_id.name == 'OTROS')
        return [{
            'currency': self.currency_id.name,
            'percent': tools.float_round(tax_igv.amount, precision),
            'amount': tools.float_round(tax_igv and tax_igv._compute_amount(
                self.price_subtotal, self.price_unit) or 0.0, precision),
            'reason_code': self.l10n_pe_exemption_reason,
            'edi_id': '1000',
            'name': 'IGV',
            'code': 'VAT',
        }, {
            'currency': self.currency_id.name,
            'percent': tools.float_round(tax_isc.amount, precision),
            'amount': tools.float_round(tax_isc and tax_isc._compute_amount(
                self.price_subtotal, self.price_unit) or 0.0, precision),
            'reason_code': self.l10n_pe_exemption_reason,
            'edi_id': '2000',
            'name': 'ISC',
            'code': 'EXC',
        }, {
            'currency': self.currency_id.name,
            'amount': tools.float_round(
                tax_otros and tax_otros._compute_amount(
                    self.price_subtotal, self.price_unit) or 0.0, precision),
            'edi_id': '9999',
            'name': 'OTROS',
            'code': 'OTH',
        }]
