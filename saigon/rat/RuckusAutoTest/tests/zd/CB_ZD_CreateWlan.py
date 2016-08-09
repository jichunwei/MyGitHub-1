"""
Description: cbZD_CreateWlan a combo test that create a list of different wlan for testing

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
    - 'wlan_cfg_list': a list of dictionary of wlan configuration to create a wlan on Zone Director
   Result type: PASS/FAIL
   Results: PASS: if all wlan create successful
            FAIL: if any wlan can't create

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

"""

import logging
from copy import deepcopy
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.common import lib_Debug as bugme


class cbZD_CreateWlan(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                          }

    def config(self, conf):
        self.conf = dict(check_status_timeout = 90,
                         check_wlan_timeout = 3,
                         pause = 2.0)

        self.conf.update(conf)
        self.errmsg = ""
        self.passmsg = ""
        self.zd = self.testbed.components['ZoneDirector']


    def test(self):
        current_wlanlist = lib.zd.wlan.get_wlan_list(self.zd)
        if current_wlanlist == None: current_wlanlist = []
        for wlan_cfg in self.conf['wlan_cfg_list']:
            if wlan_cfg['ssid'] in current_wlanlist:
                self._cfgEditWlanOnZD(wlan_cfg)
            else:
                self._cfgCreateWlanOnZD(wlan_cfg)
            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)
            self.carrierbag[wlan_cfg['ssid']] = deepcopy(wlan_cfg)

        self.passmsg = "Wlan %s create successful" % self.conf['wlan_cfg_list']
        return self.returnResult("PASS", self.passmsg)

    def cleanup(self):
        pass

    def _cfgEditWlanOnZD(self, wlan_cfg):
        logging.info("Edit WLAN [%s] with new setting on the Zone Director" % wlan_cfg['ssid'])
        lib.zd.wlan.edit_wlan(self.zd, wlan_cfg['ssid'], wlan_cfg)
        tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")

    def _cfgCreateWlanOnZD(self, wlan_cfg):
        logging.info("Create WLAN [%s] as a standard WLAN on the Zone Director" % wlan_cfg['ssid'])
        lib.zd.wlan.create_wlan(self.zd, wlan_cfg)
        tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")

