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


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Verify_Wlan_Groups_Info(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyTheWlanGroupListOnWebUI()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'expected_wlan_groups': [],
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        if self.carrierbag.get('existing_wlan_groups'):
            self.expected_wlan_group_name_list = self.carrierbag['existing_wlan_groups']
        elif self.carrierbag.get('backup_info') and self.carrierbag['backup_info'].get('existing_wlan_groups'):
            self.expected_wlan_group_name_list = self.carrierbag['backup_info']['existing_wlan_groups']
        else:
            self.expected_wlan_group_name_list = self.conf['expected_wlan_groups']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyTheWlanGroupListOnWebUI(self):
        # Verify the WLANs list show on the ZD if they are match with the expected WLANs
        wlan_group_list_on_zd = lib.zd.wgs.get_wlan_groups_list(self.zd)
        err_wlan_groups = []
        for wlan_group in self.expected_wlan_group_name_list:
            if wlan_group not in wlan_group_list_on_zd:
                err_wlan_groups.append(wlan_group)
        if err_wlan_groups:
            self.errmsg = 'The expected WLAN group(s) %s is/are not shown on the WebUI' % err_wlan_groups
            return

        self.passmsg = 'WLAN Groups %s are shown on Zone Director correctly' % wlan_group_list_on_zd
        logging.debug(self.passmsg)
