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

class CB_Station_Start_Tshark(Test):
    required_components = ['Station']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',
                         params = ' -f "udp port 67 and udp port 68" -p'
                         )
        self.conf.update(conf)
        self._retrieve_carribag()
        self.params = self.conf['params']
        self.errmsg = ""
        self.passmsg = ""
        
    
    def _retrieve_carribag(self):
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info(self.params)
        self.errmsg = eval(self.target_station.start_tshark(params = self.params))
        logging.info("Sleep 5 seconds")
        time.sleep(5)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', '')
    
    def cleanup(self):
        self._update_carribag()