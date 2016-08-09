# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)

"""

import os
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Create_Wlan_Groups(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyCreateWlanGroups()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = self.passmsg

        self._verifyTheWlanGroupListOnWebUI()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = passmsg + ', %s' % self.passmsg

        self._updateCarrierBag()

        return ('PASS', passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'num_of_wgs': 1,
                     'wlan_group_prefix': 'WLAN-GROUP',
                     'wlan_name_list': []
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyCreateWlanGroups(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:
            lib.zd.wgs.create_multi_wlan_groups(self.zd, self.conf['wlan_group_prefix'], self.conf['wlan_name_list'],
                                           num_of_wgs = self.conf['num_of_wgs'])
            self.passmsg = 'The %s WLAN Groups are created successfully' % (self.conf['num_of_wgs'])
            logging.debug(self.passmsg)
        except Exception, e:
            self.errmsg = '[WLAN groups creating failed] %s' % e.message
            logging.debug(self.errmsg)

    def _verifyTheWlanGroupListOnWebUI(self):
        # Verify the WLANs list show on the ZD if they are match with the expected WLANs
        self.wlan_group_list_on_zd = lib.zd.wgs.get_wlan_groups_list(self.zd)
        err_wlan_groups = []
        for i in range (self.conf['num_of_wgs']):
            expected_wlan_group_name = self.conf['wlan_group_prefix'] + '-%s' % (i + 1)
            if expected_wlan_group_name not in self.wlan_group_list_on_zd:
                err_wlan_groups.append(expected_wlan_group_name)
        if err_wlan_groups:
            self.errmsg = 'The expected WLAN group(s) %s is/are not shown on the WebUI' % err_wlan_groups
            return

        self.passmsg = 'WLAN Groups %s are shown on Zone Director correctly' % self.wlan_group_list_on_zd
        logging.debug(self.passmsg)

    def _updateCarrierBag(self):
        self.carrierbag['existing_wlan_groups'] = self.wlan_group_list_on_zd
