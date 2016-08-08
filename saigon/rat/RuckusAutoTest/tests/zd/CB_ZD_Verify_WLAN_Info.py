'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2012-11-1
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components import Helpers

class CB_ZD_Verify_WLAN_Info(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(wlan_info = {})
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.wlan_info = self.conf.get('wlan_info')
    
    def _retrieve_carribag(self):
        self.existed_wlan_info = self.carrierbag.get('existed_wlan_info')
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        s_t = time.time()
        while time.time() - s_t < 120:
            (res, msg) = self._verify(self.wlan_info, self.existed_wlan_info)
            if not res:
                time.sleep(3)
                logging.info("Re-get WLAN Information from ZD GUI")
                self.existed_wlan_info = Helpers.zd.wlan.get_wlan_info_detail(self.zd, 
                                                                      self.wlan_info['ssid'])
            else:
                break
            
        if res:            
            self.carrierbag['existed_wlan_info'] = self.existed_wlan_info
            return self.returnResult('PASS', 'Expected WLAN Info equal acual.')            
        else:
            self.carrierbag['existed_wlan_info'] = {}
            return self.returnResult('FAIL', msg)
    
    def _verify(self, expect_cfg, actual_cfg):
        for k, v in expect_cfg.items():
            if k in actual_cfg:
                if k in ['rxPkts', 'rxBytes']:
                    if v == 1:
                        if actual_cfg[k].strip() == "0":
                            return (False, 
                                    "expected %s!=0, but %s=%s" % (k, k, actual_cfg[k]))
                    else:
                        if actual_cfg[k].strip() != "0":
                            return (False, 
                                    "expected %s=0, but %s=%s" % (k, k, actual_cfg[k]))
                else:
                    if v != actual_cfg[k]:
                        return (False, 
                                "expected %s=%s, actual %s=%s" % (k, v, k, acutal_cfg[k]))
            else:
                return (False, "Not found Key %s in actual configuration" % k)
                
        return (True, "")
    
    def cleanup(self):
        self._update_carribag()