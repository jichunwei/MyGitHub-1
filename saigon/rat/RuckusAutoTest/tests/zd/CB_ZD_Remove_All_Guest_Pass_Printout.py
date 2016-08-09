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

class CB_ZD_Remove_All_Guest_Pass_Printout(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyRemoveAllGuestPassPrintout()
        if self.errmsg: return ('FAIL', self.errmsg)

        self.carrierbag['existing_guestpass_printout'] = []

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyRemoveAllGuestPassPrintout(self):
        try:
            guestpass_printout_on_zd = lib.zd.ga.get_list_of_guestpass_printout(self.zd)
            for gp_printout in guestpass_printout_on_zd:
                if gp_printout['name'] == 'Default':
                    continue
                lib.zd.ga.remove_guestpass_printout(self.zd, gp_printout['name'])
            self.passmsg = 'All non-default guest pass printout are deleted successfully'
            logging.debug(self.passmsg)
        except Exception, e:
            self.errmsg = '[GUESTPASS PRINTOUT DELETING ERROR]: %s' % e.message
            logging.debug(self.errmsg)
