"""
Description: CB_ZD_Create_Spoofing_Wlan a combo test that create a list of spoofing wlan for testing using broastcast SSID on the air

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

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8

class CB_ZD_Create_Spoofing_Wlan(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                          }

    def config(self, conf):
        self.conf = dict(check_status_timeout = 90,
                         check_wlan_timeout = 3,
                         pause = 2.0,
                         enable_wlan_on_default_wlan_group=True)

        self.conf.update(conf)
        self.errmsg = ""
        self.passmsg = ""
        self.zd = self.testbed.components['ZoneDirector']
        self.target_station = self.carrierbag['station']


    def test(self):
        broadcast_ssid_list = eval(self.target_station.get_visible_ssid())
        if len(broadcast_ssid_list) == 0: 
            self.errmsg = "Can not found any broadcast SSID to create Rouge Wlan"
            return self.returnResult("ERROR", self.errmsg)

        current_wlanlist = lib.zd.wlan.get_wlan_list(self.zd)
        if current_wlanlist == None: current_wlanlist = []
        for wlan_cfg in self.conf['wlan_cfg_list']:
            if wlan_cfg['ssid'] not in broadcast_ssid_list:
                wlan_cfg['ssid'] = broadcast_ssid_list[0]
            #for i in range(len(broadcast_ssid_list)):
            #    if broadcast_ssid_list[i]:
            #        wlan_cfg['ssid'] = broadcast_ssid_list[i]
            #        break

            if wlan_cfg['ssid'] in current_wlanlist:
                self._cfgEditWlanOnZD(wlan_cfg)
            else:
                self._cfgCreateWlanOnZD(wlan_cfg)
            if self.errmsg: return self.returnResult("FAIL", self.errmsg)
        if self.conf['enable_wlan_on_default_wlan_group'] == False:
            self._rmWlanOnDefaultWGS(wlan_cfg)
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
        self.errmsg = tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")

    def _cfgCreateWlanOnZD(self, wlan_cfg):
        logging.info("Create WLAN [%s] as a standard WLAN on the Zone Director" % wlan_cfg['ssid'])
        lib.zd.wlan.create_wlan(self.zd, wlan_cfg)
        self.errmsg = tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Wait for the ZD to push new configuration to the APs")

    def _rmWlanOnDefaultWGS(self, wlan_cfg):
        self.errmsg = lib.zd.wgs.uncheck_default_wlan_member( self.zd, wlan_cfg['ssid'])

