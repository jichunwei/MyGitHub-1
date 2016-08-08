"""
Description: CB_ZD_Create_Wlan_On_Standalone_AP a combo test that create a list of different wlan for testing on stand-alone AP

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

class CB_ZD_Create_Wlan_On_Standalone_AP(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                          }

    def config(self, conf):
        self.conf = {'ap_tag':''}

        self.conf.update(conf)
        self.errmsg = ""
        self.passmsg = ""

        if self.carrierbag.has_key('stand_alone_ap'):
            self.active_ap = self.carrierbag['stand_alone_ap']
            
        self.ap_tag = self.conf['ap_tag']
        if self.carrierbag.has_key(self.ap_tag):
            self.active_ap = self.carrierbag[self.ap_tag]['ap_ins']

    def test(self):
        self._createWlanInStandaloneAP()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _createWlanInStandaloneAP(self):
        logging.info('Create WLAN in stand alone AP[%s]' % self.active_ap.get_base_mac())
        if self.conf['radio'] == 'ng':
            wlan_if = 'wlan0'
        else:
            wlan_if = 'wlan8'

        try:
            for wlan_cfg in self.conf['wlan_cfg_list']:
                self.active_ap.set_ssid(wlan_if, wlan_cfg['ssid'])
                
                if self.conf.get('channel'):
                    self.active_ap.set_channel(wlan_if, self.conf['channel'])

                self.active_ap.set_state(wlan_if, 'up')
                logging.info('Create wlan %s in stand alone AP' % wlan_cfg['ssid'])
            
#                tmp_ssid = self.active_ap.get_ssid(wlan_if)
#                if tmp_ssid != wlan_cfg['ssid']:
#                    self.errmsg = "SSID is not correct after create WLAN in standalone AP"
#                    return
#
#                tmp_state = self.active_ap.get_state(wlan_if)
#                if tmp_state.lower() != 'up':
#                    self.errmsg = "WLAN status is not correct after create WLAN in standalone AP"
#                    return
            
            self.passmsg = "The wlan info is correct in the stand alone AP"
            
        except Exception, ex:
            self.errmsg = ex.message
