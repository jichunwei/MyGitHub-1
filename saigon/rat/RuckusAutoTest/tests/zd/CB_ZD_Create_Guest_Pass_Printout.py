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

class CB_ZD_Create_Guest_Pass_Printout(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)
        self._retrieve_carribag()

    def test(self):
        self._verifyCreateGuestPassPrintout()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._updateCarrierBag()

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'guestpass_printout_cfg': [],
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''
        
    def _retrieve_carribag(self):
        gprint_cfg = self.conf['guestpass_printout_cfg']
        if type(gprint_cfg) == dict and not gprint_cfg.get('html_file'):
            if self.carrierbag.has_key('gprint_cfg'):
                self.conf['guestpass_printout_cfg']['html_file'] = self.carrierbag['gprint_cfg']['html_file']
            
    def _verifyCreateGuestPassPrintout(self):
        try:
            lib.zd.ga.create_guestpass_printout(self.zd, self.conf['guestpass_printout_cfg'])
            self.passmsg = 'The authentication servers %s are created successfully' % self.conf['guestpass_printout_cfg']
            logging.debug(self.passmsg)
        except Exception, e:
            self.errmsg = '[Authentication server creating failed] %s' % e.message
            logging.debug(self.errmsg)

    def _updateCarrierBag(self):
        self.carrierbag['existing_guestpass_printout'] = lib.zd.ga.get_list_of_guestpass_printout(self.zd)
