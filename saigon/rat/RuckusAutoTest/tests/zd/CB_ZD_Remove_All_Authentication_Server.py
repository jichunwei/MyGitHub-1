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


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Remove_All_Authentication_Server(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._init_test_params(conf)


    def test(self):
        self._remove_all_auth_servers()
        if self.errmsg: return ('FAIL', self.errmsg)

        self.carrierbag['existing_authentication_sers'] = []

        return ('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        if conf.get('zd_tag'):
            self.zd = self.carrierbag[conf.get('zd_tag')]
        else:
            self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''


    def _remove_all_auth_servers(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:
            lib.zd.aaa.remove_all_servers(self.zd)
            self.passmsg = 'The authentication servers are deleted successfully'
            logging.debug(self.passmsg)

        except Exception, e:
            self.errmsg = '[Authentication server delete failed] %s' % e.message
            logging.debug(self.errmsg)

