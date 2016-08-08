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
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_Scaling_Create_Wlans(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._verifyCreateWlans()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = self.passmsg

        self._verifyTheWlanListOnWebUI()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = passmsg + ', %s' % self.passmsg
        
        self._updateCarrierBag()

        return ('PASS', passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'wlan_cfg_list': [],
                     'wlan_cfg_set': '',
                    }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        
        self.wlan_cfg_list = None
        if self.conf.get('wlan_cfg_list'):
            self.wlan_cfg_list = self.conf['wlan_cfg_list']
        else:
            self.wlan_cfg_list = tconfig.get_wlan_profile(self.conf['wlan_cfg_set'])
            

        self.errmsg = ''
        self.passmsg = ''

    def _verifyCreateWlans(self):
        # Base on the WLAN configuration list to create WLANs on ZD WebUI
        try:
            lib.zd.wlan.create_multi_wlans(self.zd, self.wlan_cfg_list)
            self.expected_wlan_name_list = [wlan['ssid'] for wlan in self.wlan_cfg_list]
            self.passmsg = 'The WLANs %s are created successfully' % self.expected_wlan_name_list
            logging.debug(self.passmsg)
        except Exception, e:
            self.errmsg = '[WLANs creating failed] %s' % e.message
            logging.debug(self.errmsg)

    def _verifyTheWlanListOnWebUI(self):
        # Verify the WLANs list show on the ZD if they are match with the expected WLANs
        self.wlan_list_on_zd = lib.zd.wlan.get_wlan_list(self.zd)
        for wlan in self.expected_wlan_name_list:
            if wlan not in self.wlan_list_on_zd:
                msg = 'The WLAN[%s] are not shown on Zone Director'
                self.errmsg = msg % wlan
                logging.debug(self.errmsg)
                return

        self.passmsg = 'WLANs %s are shown on Zone Director correctly' % self.expected_wlan_name_list
        logging.debug(self.passmsg)

    def _updateCarrierBag(self):
        self.carrierbag['existing_wlans_list'] = self.wlan_list_on_zd
