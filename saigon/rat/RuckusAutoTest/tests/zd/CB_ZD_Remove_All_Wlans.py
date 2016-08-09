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

class CB_ZD_Remove_All_Wlans(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyRemoveAllWlans()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = self.passmsg

        self._verifyTheAPsConnectedStatus()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = passmsg + ', %s' % self.passmsg

        self.carrierbag['existing_wlans_cfg'] = []

        return ('PASS', passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {
                    }
        self.conf.update(conf)
        
        zd_tag = self.conf.get('zd_tag')
        if zd_tag:
            if self.carrierbag.has_key(zd_tag):
                self.zd = self.carrierbag[zd_tag]
            else:
                raise Exception("No ZD component [%s] in carrier bag" % zd_tag)
        else:
            if self.testbed.components.has_key('ZoneDirector'):
                self.zd = self.testbed.components['ZoneDirector']
            if self.carrierbag.has_key('active_zd'):
                self.zd = self.carrierbag['active_zd']

        if self.carrierbag.get('existing_aps_connection_status'):
            self.existing_aps_connection_status = self.carrierbag['existing_aps_connection_status']
        else:
            self.existing_aps_connection_status = []

        self.errmsg = ''
        self.passmsg = ''

    def _verifyRemoveAllWlans(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:
            lib.zd.wlan.delete_all_wlans(self.zd)
            self.passmsg = 'All WLANs are deleted successfully'
            logging.debug(self.passmsg)
        except Exception, e:
            self.errmsg = '[WLANs deleting failed] %s' % e.message
            logging.debug(self.errmsg)

    def _verifyTheAPsConnectedStatus(self):
        if not self.existing_aps_connection_status:
            self.passmsg = ''
            return

        # Verify if the APs connection status be changed or not
        all_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        all_aps_connection_status = {}
        for ap in all_aps_info.keys():
            all_aps_connection_status[ap] = all_aps_info[ap]['status']
        if all_aps_connection_status != self.existing_aps_connection_status:
            errmsg = 'The connection status of APs changed to %s instead of %s'
            self.errmsg = errmsg % (all_aps_connection_status, self.existing_aps_connection_status)
            return

        self.passmsg = '[The APs connection status is correctly][%s]' % all_aps_connection_status
        logging.debug(self.errmsg)
