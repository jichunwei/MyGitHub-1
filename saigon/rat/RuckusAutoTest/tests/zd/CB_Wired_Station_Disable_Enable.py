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
        
        
Create on 2012-3-19
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers

class CB_Wired_Station_Disable_Enable(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',                        
                         )
        self.conf.update(conf)        
    
    def _retrieve_carribag(self):
#        self.sta_mac = self.carrierbag[self.conf['sta_tag']]['wired_sta_mac_addr']
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
    
    
    def _update_carribag(self):
        self.carrierbag[self.conf['sta_tag']]['wired_sta_ip_addr'] = self.ip
        self.carrierbag[self.conf['sta_tag']]['wired_sta_mac_addr'] = self.mac
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            self.target_station.disable_adapter()
            time.sleep(5)
            self.target_station.enable_adapter()
            s_t = time.time()
            while time.time() - s_t < 30:
                (self.ip, self.mac) = self.target_station.get_8021x_address()
                if self.ip or self.mac:
                    break
                  
            self._update_carribag()      
            return self.returnResult('PASS', 'Mac address %s' % self.mac)
        
        except Exception, e:
            return self.returnResult('FAIL', e.message)
    
    def cleanup(self):
        pass
        