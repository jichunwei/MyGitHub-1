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

class CB_ZD_Verify_Guest_Pass_Printout_Info(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verify_guestpass_printoutInfo()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'expected_guestpass_printout': [],
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        if self.carrierbag.get('existing_guestpass_printout'):
            self.expected_guestpass_printout_info = self.carrierbag['existing_guestpass_printout']
        elif self.carrierbag.get('backup_info') and self.carrierbag['backup_info'].get('existing_guestpass_printout'):
            self.expected_guestpass_printout_info = self.carrierbag['backup_info']['existing_guestpass_printout']
        else:
            self.expected_guestpass_printout_info = self.conf['expected_guestpass_printout']

        self.errmsg = ''
        self.passmsg = ''

    def _verify_guestpass_printoutInfo(self):
        error_gp_printout_list = []
        guestpass_printout_on_zd = lib.zd.ga.get_list_of_guestpass_printout(self.zd)
        for gp_printout in self.expected_guestpass_printout_info:
            if gp_printout not in guestpass_printout_on_zd:
                error_gp_printout_list.append(gp_printout)
        if error_gp_printout_list:
            self.errmsg = 'The guest pass printouts %s are not show on WebUI' % error_gp_printout_list
            return

        self.passmsg = 'All guest pass printouts %s are shown on WebUI correctly' % self.expected_guestpass_printout_info
