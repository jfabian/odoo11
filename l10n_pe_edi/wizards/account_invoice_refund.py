# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval


class AccountInvoiceRefund(models.TransientModel):
    """Refunds invoice"""

    _inherit = "account.invoice.refund"

    l10n_pe_refund_reason = fields.Selection([
        ('01', 'Anulación de la operación'),
        ('02', 'Anulación por error en el RUC'),
        ('03', 'Corrección por error en la descripción'),
        ('04', 'Descuento global'),
        ('05', 'Descuento por ítem'),
        ('06', 'Devolución total'),
        ('07', 'Devolución por ítem'),
        ('08', 'Bonificación'),
        ('09', 'Disminución en el valor'),
    ], help='It contains all possible values for cbc:ResponseCode',
        default='04', string="Reason for the credit note")
    l10n_pe_charge_reason = fields.Selection(
        [('01', 'Intereses por mora'),
         ('02', 'Aumento en el valor')],
        default='01', string='Debit Reason', help='Debit note reason')
    l10n_pe_edi_is_required = fields.Boolean(
        string="Is required for Peru EDI",
        help="A technical field to know whether a field could be shown",
        compute="_compute_l10n_pe_edi_is_required")

    @api.depends("filter_refund2")
    def _compute_l10n_pe_edi_is_required(self):
        required = False
        active_id = self.env.context.get('active_id', False)
        if active_id:
            invoice = self.env['account.invoice'].browse(active_id)
            required = invoice.l10n_pe_edi_is_required()
        self.l10n_pe_edi_is_required = required

    @api.model
    def _get_filter_refund_values(self):
        mode = self.env.context.get('default_filter_refund2', False)

        if mode == 'charge':
            return [('charge', 'Create a draft debit note')]

        return [('refund', 'Create a draft refund'),
                ('cancel', 'Cancel: create refund and reconcile'),
                ('modify', 'Modify: create refund, reconcile and create a '
                 'new draft invoice')]

    filter_refund = fields.Selection(
        selection_add=[('charge', 'Create a draft debit note')])
    filter_refund2 = fields.Selection(string="Refund/Charge Method",
                                      selection=_get_filter_refund_values,
                                      default='refund')

    @api.onchange('filter_refund2')
    def _onchange_filter_refund2(self):
        for obj in self:
            obj.filter_refund = obj.filter_refund2

    @api.multi
    def _get_selection_reason_label(self, field_name):
        """Get the reason label value of the field name passed in the arguments
        :param field_name: Field name type selection to obtain its label
        :return: Value that represents the field's key for the field
        """
        self.ensure_one()
        reason_codes = {k: v for k, v in self.fields_get(
            [field_name])[field_name]['selection']}
        return reason_codes[getattr(self, field_name)]

    @api.multi
    @api.onchange('l10n_pe_refund_reason')
    def _onchange_credit_reason(self):
        for wizard in self.filtered(lambda r: r.l10n_pe_edi_is_required and
                                    r.filter_refund == 'refund'):
            wizard.description = \
                wizard._get_selection_reason_label('l10n_pe_refund_reason')

    @api.onchange('l10n_pe_charge_reason')
    def _onchange_debit_reason(self):
        for wizard in self.filtered(lambda r: r.l10n_pe_edi_is_required and
                                    r.filter_refund == 'charge'):
            wizard.description = \
                wizard._get_selection_reason_label('l10n_pe_charge_reason')

    @api.multi
    def compute_refund(self, mode='refund'):
        context = dict(self.env.context or {})
        if mode == 'charge':
            context.update({
                'default_l10n_pe_charge_reason': self.l10n_pe_charge_reason,
            })
            return self.with_context(context).compute_debit_note()

        context.update({
            'default_l10n_pe_refund_reason': self.l10n_pe_refund_reason,
        })
        return super(AccountInvoiceRefund, self.with_context(context)).\
            compute_refund(mode)

    @api.multi
    def compute_debit_note(self):
        invoice = self.env['account.invoice']
        xml_id = ''
        for form in self:
            created_inv = []
            for inv in invoice.browse(self.env.context.get('active_ids')):
                date = form.date or False
                description = form.description or inv.name
                values = inv._prepare_refund(
                    inv, date=date, description=description,
                    journal_id=inv.journal_id.id)
                values.update({'type': 'out_invoice'})
                debit_invoice = self.env['account.invoice'].create(values)
                created_inv.append(debit_invoice.id)
                invoice_type = {'out_invoice': ('customer invoices debit'),
                                'in_invoice': ('vendor bill debit')}
                message = _("This %s has been created from: <a href=# "
                            "data-oe-model=account.invoice data-oe-id=%d>"
                            "%s</a>") % (
                                invoice_type[inv.type], inv.id, inv.number)
                debit_invoice.message_post(body=message)
                debit_invoice.compute_taxes()
                # Put the reason in the chatter
                debit_invoice.message_post(body=description,
                                           subject=_("Invoice debit note"))
                if inv.type in ['out_refund', 'out_invoice']:
                    xml_id = 'action_invoice_tree1'
                elif inv.type in ['in_refund', 'in_invoice']:
                    xml_id = 'action_invoice_tree2'
        if xml_id:
            result = self.env.ref('account.%s' % (xml_id)).read()[0]
            invoice_domain = safe_eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result
        return True
