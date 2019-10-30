# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_pe_edi_pse = fields.Selection(
        [('local', 'Local Service')], string="PSE Service",
        help="PSE Service the will take care of electronic documents",
        default="local")
    l10n_pe_edi_pse_test_env = fields.Boolean(
        string="Test environment",
        help="Enable the usage of test credentials",
        default=False)
    l10n_pe_edi_pse_username = fields.Char(
        string="PSE username",
        help="The username used to request the seal from the PSE")
    l10n_pe_edi_pse_password = fields.Char(
        string="PSE password",
        help="The password used to request the seal from the PSE")
    l10n_pe_edi_certificate_ids = fields.Many2many('l10n_pe_edi.certificate',
                                                   string="Certificates")
    l10n_pe_edi_sunat_username = fields.Char(
        string="SOL User", help="The username used to login to SUNAT SOL")
    l10n_pe_edi_sunat_password = fields.Char(
        string="SOL Password", help="The password used to login to SUNAT SOL")
    l10n_pe_edi_sunat_url = fields.Char(
        string='Webservice URL for invoice and notes',
        help="This URL is used to send documents like Invoices")
    l10n_pe_edi_bill_consult_url = fields.Char(
        string='Webservice URL to consult invoice and its notes',
        help="This URL is used to consult invoices and its states")
    l10n_pe_edi_sunat_auth_no = fields.Char(
        string="SUNAT authorization number",
        help="Is the number that authorize the company as PSE to emit "
        "electronic documents")
