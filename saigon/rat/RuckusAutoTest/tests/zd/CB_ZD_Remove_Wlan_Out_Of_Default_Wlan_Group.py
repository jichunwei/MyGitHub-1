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

class CB_ZD_Remove_Wlan_Out_Of_Default_Wlan_Group(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._remove_all_wlans_out_of_default_wlan_group()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = self.passmsg

        return ('PASS', passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {
                     'wlan_name_list': []
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''

    def _remove_all_wlans_out_of_default_wlan_group(self):
        try:
            wlan_members = self.conf['wlan_name_list']
            for wlan_name in wlan_members:
                lib.zd.wgs.uncheck_default_wlan_member(self.zd, wlan_name)
            self.passmsg = 'All WLANs[%s] are moved out of Default group' % wlan_members
        except Exception, e:
            self.errmsg = '[Error] %s' % e.message
