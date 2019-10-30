# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models
from odoo.exceptions import UserError


class SummaryWizard(models.TransientModel):
    _name = "l10n_pe_edi.summary.wizard"

    def _default_issue_date(self):
        return fields.Date.from_string(
            self.env['l10n_pe_edi.certificate'].
            get_pe_current_datetime().strftime("%Y-%m-%d"))

    @api.depends('summary_type')
    def _compute_number(self):
        company = self.env.user.company_id
        number = '%s-%s' % (
            self.summary_type.upper(), self.env['l10n_pe_edi.certificate'].
            get_pe_current_datetime().strftime("%Y%m%d"))
        filename = "%s-%s" % (company.partner_id.l10n_pe_vat_number, number)
        records = self.env['ir.attachment'].search(
            [('name', '=ilike', '%s%%.zip' % filename)])
        correlative = str(len(records) + 1)
        self.number = "%s-%s" % (number, correlative)

    summary_type = fields.Selection([
        ('ra', 'Voided Document'), ('rc', 'Daily Ticket Summary'),
        ('lt', 'Lot of Invoices')], default='ra', required=True,
        help="Document type to generate")
    number = fields.Char(size=20, compute="_compute_number",
                         help="Represent de number of the document")
    issue_date = fields.Date(readonly=True, default=_default_issue_date,
                             help="Date when this communication is generated.")
    reference_date = fields.Date(required=True,
                                 help="Documents date to be included.")

    def generate_document(self):
        """Generate summary document based on the summary type selected.
        :return: raise an error if any were returned while generating the
        document otherwise return the ids of attachments.
        """
        invoice_obj = self.env['account.invoice']
        vals = {'reference_date': self.reference_date, 'number': self.number,
                'issue_date': self.issue_date}
        summary_func = 'l10n_pe_edi_generate_summary_%s' % self.summary_type
        res = getattr(invoice_obj.with_context(vals), summary_func)()

        if res.get('error', False):
            raise UserError(res.get('error'))

        return res.get('attachment_ids', False)
