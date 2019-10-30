# coding: utf-8
# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
import re
from datetime import datetime

from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)

L10N_PE_REPORTS_MC = {
    '080100': 'l10n_pe.account.purchases.report',
    '080200': 'l10n_pe.account.purchases.report',
    '140100': 'l10n_pe.account.sales.report',
    'ctx_purchases': 'l10n_pe.account.context.ple.purchases',
    'ctx_sales': 'l10n_pe.account.context.ple.sales',
    'l10n_pe.account.purchases.report':
    'l10n_pe.account.context.ple.purchases',
    'l10n_pe.account.sales.report': 'l10n_pe.account.context.ple.sales'
}


class AccountReportContextCommon(models.TransientModel):
    _inherit = "account.report.context.common"  # noqa pylint: disable=consider-merging-classes-inherited

    def _report_name_to_report_model(self):
        res = super(
            AccountReportContextCommon, self)._report_name_to_report_model()
        if 'name' in self.env.context:
            if self.env.context.get('name'):
                document_name = [r for r in L10N_PE_REPORTS_MC if r
                                 in self.env.context['name']]
                if document_name:
                    res[self.env.context['name']] = L10N_PE_REPORTS_MC.get(
                        document_name[0], '')

        res['l10n_pe_purchases_report'] = L10N_PE_REPORTS_MC['080100']
        res['l10n_pe_sales_report'] = 'l10n_pe.account.sales.report'
        return res

    def _report_model_to_report_context(self):
        res = super(
            AccountReportContextCommon, self)._report_model_to_report_context()
        res['l10n_pe.account.purchases.report'] = L10N_PE_REPORTS_MC[
            'ctx_purchases']
        return res

    @api.model
    def get_full_report_name_by_report_name(self, name):
        return self.with_context(
            {'name': name})._report_name_to_report_model()[name]


class PlePurchasesReportContextPeru(models.Model):
    _inherit = "account.report.context.common"
    _name = "l10n_pe.account.context.ple.purchases"

    fold_field = 'unfolded_moves'
    unfolded_moves = fields.Many2many(
        'account.move', 'context_to_account_move_purchases_pe',
        string='Unfolded lines')
    journal_ids = fields.Many2many(
        'account.journal', relation='account_report_purchases_journals')
    available_journal_ids = fields.Many2many(
        'account.journal',
        relation='account_report_purchases_available_journal',
        default=lambda s: [(6, 0, s.env['account.journal'].search([
            ('type', '=', 'purchase')]).ids)])

    @api.multi
    def get_available_journal_ids_names_and_codes(self):
        return [[c.id, c.name, c.code] for c in self.available_journal_ids]

    @api.model
    def get_available_journals(self):
        return self.env.user.journal_ids

    def get_report_obj(self):
        return self.env['l10n_pe.account.purchases.report']

    def get_columns_names(self):
        return [_("Date"), _("Acc. Name/Number"),
                _("Debit"), _("Credit")]

    @api.multi
    def get_columns_types(self):
        return ["date", "text", "number", "number"]

    @api.multi
    def get_html_and_data(self, given_context=None):
        res = super(PlePurchasesReportContextPeru, self).get_html_and_data(
            given_context=given_context)
        xml_export_obj = self.env['account.financial.html.report.xml.export']
        res['txt_export'] = xml_export_obj.is_txt_export_available(
            self.get_report_obj())
        res['report_context']['available_journals'] = (
            self.get_available_journal_ids_names_and_codes())
        res['report_context']['journal_ids'] = self.journal_ids.ids
        return res


class PurchasesEntriesPeru(models.AbstractModel):
    _inherit = "account.general.ledger"
    _name = "l10n_pe.account.purchases.report"

    @api.model
    def get_name(self, context_id=False, has_data=False):
        return self._get_name(context_id, has_data)

    @api.model
    def _get_name(self, context_id=False, has_data=False):
        company_id = self.env.user.company_id
        ruc = '00000000' if not company_id.vat else company_id.vat[3:]
        date_from_year = ''
        date_from_month = ''
        if context_id:
            date = datetime.strptime(
                context_id.date_from, DEFAULT_SERVER_DATE_FORMAT)
            date_from_year = datetime.strftime(date, '%Y')
            date_from_month = datetime.strftime(date, '%m')
        has_data = "%(data)d" % {'data': has_data}
        report_name = '080100'
        if self.env.context.get('report_id', '') == '2':
            report_name = '080200'
        if self.env.context.get('sales_report', ''):
            report_name = '140100'
        return 'LE%s%s%s00%s001%s11' % (ruc, date_from_year, date_from_month,
                                        report_name, has_data)

    @api.model
    def get_lines(self, context_id, line_id=None, just_grouped=False):
        new_context = self.get_context_for_lines(context_id, line_id)
        return self.with_context(new_context)._lines(line_id, just_grouped)

    def get_context_for_lines(self, context_id, line_id=None):
        if isinstance(context_id, int):
            context_id = self.env[
                L10N_PE_REPORTS_MC[self.env.context['model']]].search(
                    [['id', '=', context_id]])
        new_context = dict(self.env.context)
        new_context.update({
            'date_from': context_id.date_from,
            'date_to': context_id.date_to,
            'state': context_id.all_entries and 'all' or 'posted',
            'cash_basis': context_id.cash_basis,
            'context_id': context_id,
            'company_ids': context_id.company_ids.ids,
            'journal_ids': context_id.journal_ids.ids,
            'analytic_account_ids': context_id.analytic_account_ids,
            'analytic_tag_ids': context_id.analytic_tag_ids,
            'available_journal_ids': context_id.available_journal_ids,
        })
        return new_context

    @api.model
    def get_title(self):
        return _("PLE Purchases Report")

    def group_by_journal_id(self, line_id, journal_type='purchase'):
        journals = {}
        context = self.env.context
        move_obj = self.env['account.move.line']
        journal_ids = self.env['account.journal'].browse(
            context.get('journal_ids', []))

        if not journal_ids:
            journal_ids = self.env['account.journal'].search([
                ('type', '=', journal_type)])

        for journal in journal_ids:
            journals[journal] = {}
            domain = [
                ('date', '<=', context['date_to']),
                ('company_id', 'in', context['company_ids']),
                ('journal_id', '=', journal.id)]
            if context['date_from_aml']:
                domain.append(('date', '>=', context['date_from_aml']))
            if context['state'] == 'posted':
                domain.append(('move_id.state', '=', 'posted'))
            if not context.get('print_mode'):
                #  fetch the 81 first amls. The report only displays the first
                # 80 amls. We will use the 81st to know if there are more than
                # 80 in which case a link to the list view must be displayed.
                journals[journal]['lines'] = move_obj.search(
                    domain, order='date', limit=81)
            else:
                journals[journal]['lines'] = move_obj.search(
                    domain, order='date')
        return journals

    @api.model
    def _lines(self, line_id=None, just_grouped=False):
        lines = []
        if line_id:
            lines.extend(self._get_lines_second_level(
                self.env['account.move'].browse(line_id)))
            return lines
        context = self.env.context
        company_id = context.get('company_id') or self.env.user.company_id
        # TODO if this report becames too slow we need to make a psql query
        grouped_journals = self.with_context(
            date_from_aml=context['date_from'],
            date_from=context['date_from'] and
            company_id.compute_fiscalyear_dates(datetime.strptime(
                context['date_from'],
                DEFAULT_SERVER_DATE_FORMAT))['date_from'] or
            None).group_by_journal_id(line_id)
        if just_grouped:
            return grouped_journals
        sorted_journals = sorted(grouped_journals, key=lambda a: a.code)
        move_lines = self.env['account.move']
        for journal in sorted_journals:
            if not grouped_journals[journal].get('lines', []):
                continue
            move_lines |= (
                grouped_journals[journal]['lines']).mapped('move_id')
        partners = move_lines.mapped('partner_id')
        for partner in partners:
            invoices_ids = move_lines.filtered(
                lambda r: r.partner_id == partner)
            partner_vat = partner.vat or '00000000'
            name = "%(name)s --- %(vat)s" % (
                {'name': partner.name,
                 'vat': partner_vat})
            lines.append({
                'id': partner.id,
                'type': 'line',
                'name': name,
                'footnotes': {},
                'columns': [],
                'level': 1,
                'unfoldable': False,
                'unfolded': True,
                'colspan': 6,
            })
            lines.extend(self._get_lines_second_level(invoices_ids))
        return lines

    @api.model
    def _get_lines_second_level(self, move_ids):
        lines = []
        context = self.env.context
        unfold_all = context.get('print_mode') and not context[
            'context_id']['unfolded_moves']
        for move in move_ids:
            name = move.name
            name = name
            context = self.env.context
            lines.append({
                'id': move.id,
                'type': 'line',
                'name': name,
                'footnotes': {},
                'columns': [move.date, '', '', ''],
                'level': 2,
                'unfoldable': True,
                'unfolded': move in context['context_id'][
                    'unfolded_moves'] or unfold_all,
            })
            if move in context['context_id'][
                    'unfolded_moves'] or unfold_all:
                lines.extend(self._get_lines_third_level(move))
        return lines

    @api.model
    def _get_lines_third_level(self, move):
        lines = []
        for line in move.line_ids:
            name = line.name
            name = name
            acc_name = line.account_id.display_name
            acc_name = (acc_name[:35] + "..." if len(acc_name) > 35 else
                        acc_name)
            lines.append({
                'id': line.id,
                'move_id': move.id,
                'action': line.get_model_id_and_name(),
                'type': 'move_line_id',
                'name': name,
                'footnotes': {},
                'columns': [
                    '', acc_name,
                    line.debit, line.credit],
                'level': 3,
            })
        return lines


class AccountFinancialReportXMLExport(models.AbstractModel):
    _inherit = "account.financial.html.report.xml.export"  # noqa pylint: disable=consider-merging-classes-inherited

    @api.multi
    def is_txt_export_available(self, report_obj):
        if report_obj._name in L10N_PE_REPORTS_MC.values():
            return True
        return False

    @api.model
    def check(self, report_name, report_id=None):
        if report_name == L10N_PE_REPORTS_MC['080100']:
            return True
        return super(AccountFinancialReportXMLExport, self).check(
            report_name, report_id=report_id)

    def do_xml_export(self, context):
        if context.get_report_obj()._name == L10N_PE_REPORTS_MC['080100']:
            return self._l10n_pe_ple_purchases_txt_export(context)
        return super(
            AccountFinancialReportXMLExport, self).do_xml_export(context)

    def _l10n_pe_ple_purchases_txt_export(self, context):
        grouped_journals = context.get_report_obj().with_context(
            print_mode=True).get_lines(context, just_grouped=True)
        sorted_journals = sorted(grouped_journals, key=lambda a: a.code)
        moves = self.env['account.move']

        for journal in sorted_journals:
            if not grouped_journals[journal].get('lines', []) or (
                self.env.context.get('report_id', '') == '2' and not
                    journal.filtered(lambda r: 'FPND' in r.code)):
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

            serie_folio = self._l10n_pe_get_serie_and_folio(
                invoice.move_id.name)
            report += "%(date).6s00|" % (
                {'date': context.date_from.replace('-', '')})
            report += "%(date).6s-C-%(folio)s|" % ({
                'date': context.date_from.replace('-', ''),
                'folio': serie_folio['folio']})
            report += 'M%s|' % serie_folio['folio']
            report += datetime.strptime(
                invoice.date, fields.DATE_FORMAT).strftime('%d/%m/%Y') + '||'
            report += invoice.l10n_pe_document_type or '01' + '|'  # TODO
            report += (invoice.l10n_pe_edi_serie if
                       invoice.l10n_pe_edi_serie else '0001') + "||"
            report += serie_folio['folio'] + '||'

            report += (invoice.partner_id.l10n_pe_edi_vat_code or '0') + '|'
            report += (
                invoice.partner_id.l10n_pe_vat_number or '00000000') + '|'
            report += invoice.partner_id.name + '|'
            report += "%(untaxed)s|" % {'untaxed': invoice.amount_untaxed}
            report += "%(amount_tax)d|" % {'amount_tax': invoice.amount_tax}
            report += '|' * 4
            report += "%(amount_unaffected)d|" % {
                'amount_unaffected': invoice.l10n_pe_edi_amount_unaffected}

            report += '|'  # We don't have ISC
            report += "%(total_otros)d|" % {
                'total_otros': invoice.l10n_pe_edi_total_otros}
            report += "%(amount_total)d|" % {
                'amount_total': invoice.amount_total}
            report += "%(currency_name)s|" % {
                'currency_name': invoice.currency_id.name}
            report += '%(name).3f' % ({'name': invoice.currency_id.rate}) + '|'
            report += (
                datetime.strptime(related.date_invoice,
                                  fields.DATE_FORMAT).strftime(
                                      '%d/%m/%Y') if related else '') + '|'
            report += (related.l10n_pe_document_type if related else '') + '|'
            report += (related.move_name if related else '') + '||'
            report += (related.l10n_pe_edi_serie if related else '') + '|'

            report += '|' * 3  # Deductions
            report += '|'  # TODO
            report += '|' * 5
            report += '|'  # TODO

            report += self.document_identity(invoice, context) + '|\n'
        return report

    def document_identity(self, document, context):
        """Given the date of the document:
            if it belongs to a previous date of report, return 6, for any other
            case return 1. The other options for this report are not listed
            because at the moment it does not apply to odoo-peru.
        """
        if (datetime.strptime(document.date[:-3], "%Y-%m") <
                datetime.strptime(context.date_from[:-3], "%Y-%m")):
            return '6'
        return '1'

    @staticmethod
    def _l10n_pe_get_serie_and_folio(number):
        values = {'serie': None, 'folio': None}
        number_matchs = [rn for rn in re.finditer('\\d+', number or '')]
        if number_matchs:
            last_number_match = number_matchs[-1]
            values['serie'] = number[:last_number_match.start()] or None
            values['folio'] = last_number_match.group() or None
        return values
