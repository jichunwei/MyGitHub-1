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

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Remove_All_L3_ACLs_IPV6(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._remove_all_l3_ipv6_acls()
        
        if self.errmsg: 
            return ('FAIL', self.errmsg)
        else:
            self.carrierbag['existing_l3_acls'] = []
            return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''

    def _remove_all_l3_ipv6_acls(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:
            lib.zd.ac.delete_all_l3_ipv6_acl_policies(self.zd)
            self.passmsg = 'All L3 IPV6 ALCs are deleted successfully'
            logging.debug(self.passmsg)
        except Exception, e:
            self.errmsg = '[DELETE ALL L3 IPV6 ALCs ERROR] %s' % e.message
            logging.debug(self.errmsg)
