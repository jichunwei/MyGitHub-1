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

class CB_ZD_Verify_L3_ACLs_Info(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyL3ACLsInfo()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'expected_l3_acls': [],
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if 'active_zd' in self.carrierbag:
            self.zd = self.carrierbag['active_zd']

        if self.carrierbag.get('existing_l3_acls'):
            self.expected_l3_acls_info = self.carrierbag['existing_l3_acls']
        elif self.carrierbag.get('backup_info') and self.carrierbag['backup_info'].get('existing_l3_acls'):
            self.expected_l3_acls_info = self.carrierbag['backup_info']['existing_l3_acls']
        else:
            self.expected_l3_acls_info = self.conf['expected_l3_acls']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyL3ACLsInfo(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        err_acls = []
        all_l3_acls_on_zd = lib.zd.ac.get_all_l3_acl_policies(self.zd)
        for acl in self.expected_l3_acls_info:
            if acl not in all_l3_acls_on_zd:
                err_acls.append(acl)
        if err_acls:
            self.errmsg = 'The L3 ACLs %s are not shown on the WebUI' % err_acls
            return

        self.passmsg = 'The L3 ACLs %s are shown on WebUI correctly' % self.expected_l3_acls_info
