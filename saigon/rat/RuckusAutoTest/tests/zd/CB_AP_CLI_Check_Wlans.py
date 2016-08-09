'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - initialize parameter.
   2. Test:
       - check number of ssids
   3. Cleanup:
       - None
    How it was tested:
        
        
Create on 2013-1-10
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.apcli import radiogroup


class CB_AP_CLI_Check_Wlans(Test):
    required_components = ['RuckusAP']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(num_of_ssids=64,
                         ap_tag = 'AP_01'
                         )
        self.conf.update(conf)
    
    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf.get('ap_tag')]['ap_ins']        
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        import time
        st = time.time()
        while time.time() - st < 230:
            wlan_list = radiogroup.get_wlanlist(self.active_ap)            
            cnt = 0
            for wlan in wlan_list:
                if 'AP' == wlan.get('type') and 'up' == wlan.get('status') and '00:00:00:00:00:00' != wlan.get('bssid') and (not 'mesh' in wlan.get('name')):
                    cnt += 1
            
            if self.conf.get('num_of_ssids') == cnt:
                return self.returnResult('PASS', 'The WLANs status is correct')
            else:
                time.sleep(10)
        if 'wlan_list' in locals():
            logging.info(wlan_list)
                
        return self.returnResult('FAIL', 'The WLANs status is incorrect, please check')
    
    
    def cleanup(self):
        self._update_carribag()