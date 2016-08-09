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

class CB_Wired_Station_Perform_Auth(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',
                         username = 'ras.local.user',
                         password = 'ras.local.user',
                         )
        self.conf.update(conf)        
    
    def _retrieve_carribag(self):
        self.sta_ins = self.carrierbag[self.conf['sta_tag']]['sta_ins']
    
    def _update_carribag(self):
        self.carrierbag[self.conf['sta_tag']]['wired_sta_ip_addr'] = self.ip
        self.carrierbag[self.conf['sta_tag']]['wired_sta_mac_addr'] = self.mac
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        cnt = 3
        while cnt:
            try:
#                self.sta_ins.disable_adapter()
#                time.sleep(5)
#                self.sta_ins.enable_adapter()
#                time.sleep(5)
                res  = eval(self.sta_ins.auth_wire_sta(self.conf['username'], 
                                                       self.conf['password']))
#                time.sleep(3)
                break
            except:
                cnt = cnt - 1
                
        (ip, mac) = self.sta_ins.get_8021x_address()        
        if ip:
            self.ip = ip
            self.mac = mac
            self._update_carribag()
            return self.returnResult('PASS', 'Authentication is DONE.')        
        else:
            return self.returnResult("FAIL", "Haven't get ip address.")
    
    def cleanup(self):
        pass
        