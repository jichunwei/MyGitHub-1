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

class CB_Wired_Station_Remove(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',                        
                         )
        self.conf.update(conf)  
        self.zd = self.testbed.components['ZoneDirector']      
    
    def _retrieve_carribag(self):
        self.sta_mac = self.carrierbag[self.conf['sta_tag']]['wired_sta_mac_addr']
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            Helpers.zd.awc.delete_clients(self.zd, self.sta_mac)
            return self.returnResult("PASS", "Remove wire client %s" % self.sta_mac)
        except Exception, e:
            return self.returnResult("FAIL", e.message)
    
    def cleanup(self):
        pass
        