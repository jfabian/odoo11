# -*- coding: utf-8 -*-

from odoo.tests import common


class TestAutoFill(common.TransactionCase):

    def setUp(self):
        super(TestAutoFill, self).setUp()

        self.partner = self.env.ref('base.partner_root')
        self.district = self.env.ref('l10n_pe_toponyms.PE250106')

    def test_auto_fill(self):

        # Check previous distric
        self.assertFalse(self.partner.l10n_pe_district_id,
                         'This partner has already a district set')

        # Set a district
        self.partner.l10n_pe_district_id = self.district

        # Check province
        self.assertFalse(self.partner.l10n_pe_province_id,
                         'This partner has already a province '
                         'set without onchange')

        # Use onchange
        self.partner.onchange_l10n_pe_district_id()
        # Check province and state
        self.assertTrue(self.partner.l10n_pe_province_id and
                        self.partner.state_id,
                        'The fields province and state are not set')

        # Check province and state
        self.assertEquals(self.partner.l10n_pe_district_id.province_id,
                          self.partner.l10n_pe_province_id,
                          'The field province not allow to the district set')

        # Check province and state
        self.assertEquals(self.partner.state_id,
                          self.partner.l10n_pe_province_id.state_id,
                          'The field state not allow to the province set')
