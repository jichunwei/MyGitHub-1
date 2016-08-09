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
        
        
Create on 2012-2-20
@author: cwang@ruckuswireless.com
'''

import logging
import time
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

class CB_Server_Stop_Tshark(Test):
    required_components = ['LinuxServer']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.sniffer = self.testbed.components['LinuxServer']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            logging.info("Sleep 10 seconds to make sure package is generated")
            time.sleep(10)
            self.sniffer.stop_tshark()
        except Exception, ex:
            return self.returnResult("FAIL", ex.message)
        
        return self.returnResult('PASS', '')
    
    def cleanup(self):
        self._update_carribag()