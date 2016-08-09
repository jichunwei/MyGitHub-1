"""
   Description: 
   This test class support to verify the 80211debug message for the background scanning
   @since: Jun 2013
   @author: An Nguyen

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get the DHCP lease time of special station from AP and check the lease time      
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Verify DHCP lease time on AP success 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
      
class CB_AP_CLI_Enable_80211debug_Mode(Test):
    required_components = ['RuckusAP','Station']
    parameters_description = {'scan': True,
                              'ap_tag' : 'active_ap',
                              }

    def config(self, conf):
        self._cfg_init_test_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        self._enable_80211debug_mode()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            logging.debug(self.passmsg)
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
            
    def _cfg_init_test_params(self, conf):
        self.conf = {'scan': True,
                     'ap_tag' : 'active_ap',}
        
        self.conf.update(conf)
       
        self.errmsg = ''
        self.passmsg = ''
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']
   
    def _enable_80211debug_mode(self):
        logging.info('Enable 80211debug mode on AP %s' % self.active_ap.base_mac_addr)
        active_wlan_list = []
        wlanlist = lib.apcli.radiogrp.get_wlanlist(self.active_ap)
        for wlan in wlanlist:
            if wlan['type'] == 'AP' and wlan['status'] == 'up':
                active_wlan_list.append(wlan['wlanid'])
                logging.info('Enable 80211debug mode on %s' % wlan['wlanid']) 
                lib.apcli.shell.enable_80211debug_mode(self.active_ap, wlan['wlanid'], self.conf['scan'])
                
        if not active_wlan_list:
            self.errmsg = '[INCORRECT BEHAVIOR] There is not any active wlan on APs. Please check!'
            return
              
        self.passmsg = 'Enabled 80211debug for wlan %s successfully' % active_wlan_list