# coding: utf-8
# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from datetime import datetime

from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from .account_purchases_ple import L10N_PE_REPORTS_MC

_logger = logging.getLogger(__name__)


class AccountReportContextCommon(models.TransientModel):
    _inherit = "account.report.context.common"  # noqa pylint: disable=consider-merging-classes-inherited

    def _report_model_to_report_context(self):
        res = super(
            AccountReportContextCommon, self)._report_model_to_report_context()
        res['l10n_pe.account.sales.report'] = L10N_PE_REPORTS_MC['ctx_sales']
        return res


class PleSalesReportContextPeru(models.Model):
    _inherit = "account.report.context.common"
    _name = "l10n_pe.account.context.ple.sales"

    fold_field = 'unfolded_moves'
    unfolded_moves = fields.Many2many(
        'account.move', 'context_to_account_move_sale_pe',
        string='Unfolded lines')
    journal_ids = fields.Many2many(
        'account.journal', relation='account_report_sale_journals')
    available_journal_ids = fields.Many2many(
        'account.journal', relation='account_report_sale_available_journal',
        default=lambda s: [(6, 0, s.env['account.journal'].search([
            ('type', '=', 'sale')]).ids)])

    @api.multi
    def get_available_journal_ids_names_and_codes(self):
        return [[c.id, c.name, c.code] for c in self.available_journal_ids]

    @api.model
    def get_available_journals(self):
        return self.env.user.journal_ids

    def get_report_obj(self):
        return self.env[L10N_PE_REPORTS_MC['140100']]

    def get_columns_names(self):
        return [_("Date"), _("Acc. Name/Number"),
                _("Debit"), _("Credit")]

    @api.multi
    def get_columns_types(self):
        return ["date", "text", "number", "number"]

    @api.multi
    def get_html_and_data(self, given_context=None):
        res = super(PleSalesReportContextPeru, self).get_html_and_data(
            given_context=given_context)
        xml_export_obj = self.env['account.financial.html.report.xml.export']
        res['txt_export'] = xml_export_obj.is_txt_export_available(
            self.get_report_obj())
        res['report_context']['available_journals'] = (
            self.get_available_journal_ids_names_and_codes())
        res['report_context']['journal_ids'] = self.journal_ids.ids
        return res


class SalesEntriesPeru(models.AbstractModel):
    _inherit = "account.general.ledger"
    _name = "l10n_pe.account.sales.report"

    @api.model
    def get_name(self, context_id=False, has_data=False):
        return self.env['l10n_pe.account.purchases.report'].with_context(
            {'sales_report': True})._get_name(context_id, has_data)

    @api.model
    def get_lines(self, context_id, line_id=None, just_grouped=False):
        purchases_obj = self.env['l10n_pe.account.purchases.report']
        new_context = purchases_obj.get_context_for_lines(context_id, line_id)
        return self.with_context(new_context)._lines(line_id, just_grouped)

    @api.model
    def get_title(self):
        return _("PLE Sales Report")

    @api.model
    def _lines(self, line_id=None, just_grouped=False):
        lines = []
        purchases_obj = self.env['l10n_pe.account.purchases.report']
        if line_id:
            lines.extend(purchases_obj._get_lines_second_level(
                self.env['account.move'].browse(line_id)))
            return lines
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        grouped_journals = purchases_obj.with_context(
            date_from_aml=context['date_from'],
            date_from=context['date_from'] and
            company_id.compute_fiscalyear_dates(datetime.strptime(
                context['date_from'], DEFAULT_SERVER_DATE_FORMAT))[
                    'date_from'] or None).group_by_journal_id(line_id, 'sale')
        if just_grouped:
            return grouped_journals
        sorted_journals = sorted(grouped_journals, key=lambda a: a.code)
        for journal in sorted_journals:
            if not grouped_journals[journal].get('lines', []):
                continue
            lines.append({
                'id': journal.id,
                'type': 'line',
                'name': journal.name,
                'footnotes': {},
                'columns': [],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
                'colspan': 6,
            })
            lines.extend(purchases_obj._get_lines_second_level(
                grouped_journals[journal].get('lines', []).mapped('move_id')))
        return lines


class AccountFinancialReportXMLExport(models.AbstractModel):
    _inherit = "account.financial.html.report.xml.export"  # noqa pylint: disable=consider-merging-classes-inherited

    @api.model
    def check(self, report_name, report_id=None):
        if report_name == L10N_PE_REPORTS_MC['140100']:
            return True
        return super(AccountFinancialReportXMLExport, self).check(
            report_name, report_id=report_id)

    def do_xml_export(self, context):
        if context.get_report_obj()._name == L10N_PE_REPORTS_MC['140100']:
            return self._l10n_pe_ple_sales_txt_export(context)
        return super(
            AccountFinancialReportXMLExport, self).do_xml_export(context)

    def _l10n_pe_ple_sales_txt_export(self, context):
        grouped_journals = context.get_report_obj().with_context(
            print_mode=True).get_lines(context, just_grouped=True)
        sorted_journals = sorted(grouped_journals, key=lambda a: a.code)
        moves = self.env['account.move']
        purchases_obj = self.env['account.financial.html.report.xml.export']

        for journal in sorted_journals:
            if not grouped_journals[journal].get('lines', []):
                continue
            moves += grouped_journals[
                journal].get('lines', []).mapped('move_id')
        invoices = self.env['account.invoice'].search(
            [('move_id', 'in', moves.ids)])

        report = ''
        related = None
        for invoice in invoices:
            if invoice.l10n_pe_document_type in ['07', '08']:
                related = invoice.refund_invoice_id
            serie_folio = purchases_obj._l10n_pe_get_serie_and_folio(
                invoice.move_id.name)
            report += "%(date).6s00|" % (
                {'date': context.date_from.replace('-', '')})
            report += "%(date).6s-V-%(folio)s|" % ({
                'date': context.date_from.replace('-', ''),
                'folio': serie_folio['folio']})
            report += 'M%s|' % serie_folio['folio']
            report += (datetime.strptime(
                invoice.date_invoice,
                fields.DATE_FORMAT).strftime(
                    '%d/%m/%Y') if invoice else '') + '||'
            report += (invoice.l10n_pe_document_type or '') + '|'
            report += (invoice.l10n_pe_edi_serie if
                       invoice.l10n_pe_edi_serie else '0001') + "|"
            report += (
                invoice.l10n_pe_edi_correlative or serie_folio['folio']) + '||'
            report += (invoice.partner_id.l10n_pe_edi_vat_code or '0') + '|'
            report += (invoice.partner_id.l10n_pe_vat_number or
                       '00000000') + '|'
            report += invoice.partner_id.name + '||'
            report += "%(amount_tax)d|" % {'amount_tax': invoice.amount_tax}
            report += "%(discounts)d|||" % {
                'discounts': invoice.l10n_pe_edi_total_discounts}
            report += "%(discounts)d|" % {
                'discounts': invoice.l10n_pe_edi_amount_exonerated}
            report += "%(amount_unaffected)d||||" % {
                'amount_unaffected': invoice.l10n_pe_edi_amount_unaffected}
            report += "%(total_otros)d|" % {
                'total_otros': invoice.l10n_pe_edi_total_otros}
            report += "%(amount_total)d|" % {
                'amount_total': invoice.amount_total}
            report += "%(currency_name)s|" % {
                'currency_name': invoice.currency_id.name}
            report += '%(name).3f|' % ({'name': invoice.currency_id.rate})
            report += (related.date_invoice if related else '') + '|'
            report += (related.l10n_pe_document_type if related else '') + '|'
            report += (related.move_name if related else '') + '|||||'
            report += '1|\n'  # TODO
        return report
