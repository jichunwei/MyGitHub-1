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

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib



# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Verify_APs_Info(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._verify_aps_info()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'expected_ap_info': [],
                     'zd_tag':''
                    }
        self.conf.update(conf)
        zd_tag = self.conf.get('zd_tag')
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']

        if self.carrierbag.get('existing_aps_info'):
            self.expected_aps_info = self.carrierbag['existing_aps_info']
        elif self.carrierbag.get('backup_info') and self.carrierbag['backup_info'].get('existing_aps_info'):
            self.expected_aps_info = self.carrierbag['backup_info']['existing_aps_info']
        else:
            self.expected_aps_info = self.conf['expected_ap_info']

        self.errmsg = ''
        self.passmsg = ''

    def _verify_aps_info(self):
        if self.expected_aps_info:
            self._verify_expected_aps_info()
        else:
            self._verify_all_aps_connected()

    def _verify_expected_aps_info(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        err_aps = []
        all_aps_on_zd = lib.zd.ap.get_all_ap_info(self.zd)
        for ap in self.expected_aps_info.keys():
            for key in self.expected_aps_info[ap].keys():
                if ap[key] != all_aps_on_zd[ap][key]:
                    err_aps.append(ap)
        if err_aps:
            self.errmsg = 'The APs %s info are not same as expected' % err_aps
            return

        self.passmsg = 'The APs %s are shown on WebUI correctly' % self.expected_aps_info

    def _verify_all_aps_connected(self):
        err_aps = []
        all_aps_on_zd = lib.zd.ap.get_all_ap_info(self.zd)
        for ap in all_aps_on_zd.keys():
            if 'Connected' not in all_aps_on_zd[ap]['status']:
                err_aps.append(ap)
        if err_aps:
            self.errmsg = 'The APs %s are not connected to the system' % err_aps
            return

        self.passmsg = 'All APs are connected to the system'