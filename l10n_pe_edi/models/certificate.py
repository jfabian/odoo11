# coding: utf-8
# Copyright 2017 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import base64
import logging
import ssl
from datetime import datetime

from pytz import timezone

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)
try:
    from OpenSSL import crypto
except ImportError:
    _logger.warning('OpenSSL library not found. If you plan to use '
                    'l10n_pe_edi, please install the library from '
                    'https://pypi.python.org/pypi/pyOpenSSL')


def str_to_datetime(dt_str, tztz=timezone('America/Lima')):
    return tztz.localize(fields.Datetime.from_string(dt_str))


class Certificate(models.Model):
    _name = 'l10n_pe_edi.certificate'
    _description = 'Sunat Digital Sail'
    _order = 'date_start desc, id desc'

    content = fields.Binary(
        string="Certificate",
        help='PFX Certificate',
        required=True)
    password = fields.Char(
        string="Certificate Password",
        help='Passphrase for the PFX certificate',
        required=True)
    serial_number = fields.Char(
        help='The serial number to add to electronic documents',
        readonly=True,
        index=True)
    date_start = fields.Datetime(
        string='Available date',
        help='The date on which the certificate starts to be valid',
        readonly=True)
    date_end = fields.Datetime(
        string='Expiration date',
        help='The date on which the certificate expires',
        readonly=True)

    @api.multi
    @tools.ormcache('content', 'password')
    def get_x509_cert(self, content, password):
        """Get the certificate"""
        self.ensure_one()
        return crypto.load_pkcs12(base64.b64decode(content), password)

    @api.multi
    @tools.ormcache('content', 'password')
    def get_pem_cert(self, content, password):
        """Get the current content in PEM format
        """
        self.ensure_one()
        cert_x509 = self.get_x509_cert(content, password).get_certificate()
        return crypto.dump_certificate(crypto.FILETYPE_PEM, cert_x509)

    @api.multi
    @tools.ormcache('content', 'password')
    def get_pem_key(self, content, password):
        """Get the current key in PEM format
        """
        self.ensure_one()
        key_x509 = self.get_x509_cert(content, password).get_privatekey()
        return crypto.dump_privatekey(crypto.FILETYPE_PEM, key_x509)

    @api.multi
    def get_pe_current_datetime(self):
        """Get the current datetime with the Mexican timezone.
        """
        peruvian_tz = timezone('America/Lima')
        return datetime.now(peruvian_tz)

    @api.multi
    def get_valid_certificate(self):
        """Search for a valid certificate that is available and not expired.
        """
        peruvian_dt = self.get_pe_current_datetime()
        for record in self:
            date_start = str_to_datetime(record.date_start)
            date_end = str_to_datetime(record.date_end)
            if date_start <= peruvian_dt <= date_end:
                return record
        return None

    @api.multi
    def get_data(self):
        """Return the content (DER encoded) and the certificate decrypted
        based on https://goo.gl/IpeFQZ
        """
        self.ensure_one()
        content = self.content
        password = self.password
        cert_x509 = self.get_x509_cert(content, password).get_certificate()
        cert_pem = self.get_pem_cert(content, password)
        key_pem = self.get_pem_key(content, password)
        for to_del in ['\n', ssl.PEM_HEADER, ssl.PEM_FOOTER]:
            cert_pem = cert_pem.replace(to_del, '')
        return cert_pem, key_pem, cert_x509

    @api.multi
    @api.constrains('content', 'password')
    def _check_credentials(self):
        """Check the validity of content/key/password and fill the fields
        with the certificate values.
        """
        peruvian_tz = timezone('America/Lima')
        peruvian_dt = self.get_pe_current_datetime()
        date_format = '%Y%m%d%H%M%SZ'
        for record in self:
            # Try to decrypt the certificate
            try:
                cert_pem, key_pem, certificate = record.get_data()
                before = peruvian_tz.localize(
                    datetime.strptime(certificate.get_notBefore(),
                                      date_format))
                after = peruvian_tz.localize(
                    datetime.strptime(certificate.get_notAfter(), date_format))
                serial_number = certificate.get_serial_number()
            except Exception:
                raise ValidationError(_('The certificate content is invalid.'))
            # Assign extracted values from the certificate
            record.serial_number = ('%x' % serial_number)[1::2]
            record.date_start = before.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            record.date_end = after.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            if peruvian_dt > after:
                raise ValidationError(_('The certificate is expired since %s')
                                      % record.date_end)

            # Check the pair key and cert exists
            if not cert_pem or not key_pem:
                raise ValidationError(_('The certificate or key are missing '
                                        'from the PKCS#12 file.'))

    @api.model
    def create(self, data):
        res = super(Certificate, self).create(data)
        self.clear_caches()
        return res

    @api.multi
    def write(self, data):
        res = super(Certificate, self).write(data)
        self.clear_caches()
        return res

    @api.multi
    def unlink(self):
        res = super(Certificate, self).unlink()
        self.clear_caches()
        return res
