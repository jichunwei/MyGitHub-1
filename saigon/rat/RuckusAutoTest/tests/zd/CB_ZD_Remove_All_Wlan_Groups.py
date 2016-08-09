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

class CB_ZD_Remove_All_Wlan_Groups(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyRemoveAllWlanGroups()
        if self.errmsg: return ('FAIL', self.errmsg)

        self.carrierbag['existing_wlan_groups'] = []

        return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'zd_tag': '',
                     'is_ap_on_zd': True, #If false, means no AP on zd, don't need to 
                                          # change ap group to default before remove wlan group. 
                     }
        self.conf.update(conf)
        
        zd_tag = self.conf['zd_tag']
        if zd_tag:
            self.zd = self.carrierbag[zd_tag]
        else:
            self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''
        self.passmsg = ''

    def _verifyRemoveAllWlanGroups(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:
            logging.info("Remove all WLAN Groups on the Zone Director.")
            if self.conf['is_ap_on_zd']:
                lib.zd.wgs.remove_wlan_groups(self.zd, self.testbed.get_aps_sym_dict_as_mac_addr_list())
            else:
                #If no ap on ZD, don't need to edit ap.
                lib.zd.wgs.remove_wlan_groups(self.zd, [])
                
            self.passmsg = 'All WLAN Groups are deleted successfully'
            logging.debug(self.passmsg)
        except Exception, e:
            self.errmsg = '[WLAN Groups deleting failed] %s' % e.message
            logging.debug(self.errmsg)
