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
from RuckusAutoTest.components import Helpers


class CB_ZD_Delete_Wired_Client(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1')
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.sta_tag = self.conf['sta_tag']
        
    
    def _retrieve_carribag(self):
        self.sta_ins = self.carrierbag[self.conf['sta_tag']]['sta_ins']
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            Helpers.zd.awc.delete_clients(self.zd, "")
            self.sta_ins.disable_adapter()
            time.sleep(10)
            self.sta_ins.enable_adapter()
            time.sleep(30)
            return self.returnResult('PASS', 'All of wired client have been deleted')
        except Exception, e:            
            return self.returnResult('FAIL', e.message)
    
    def cleanup(self):
        self._update_carribag()