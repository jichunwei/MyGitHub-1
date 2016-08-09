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


class CB_Server_Start_Tshark(Test):
    required_components = ['LinuxServer']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(params = ' -f "udp port 67 and udp port 68"')
        self.conf.update(conf)
        self.params = self.conf['params']
        self.sniffer = self.testbed.components['LinuxServer']
        if "-i " not in self.params:#Auto-detect interface.
            self.svr_ip_addr = self.sniffer.ip_addr
            server_interface = self.sniffer.get_interface_name_by_ip(self.svr_ip_addr)
            self.params = " -i %s %s" % (server_interface, self.params)
            logging.info(self.params)
        
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:    
            logging.info(self.params)        
            self.sniffer.start_tshark(self.params)
            logging.info("Sleep 5 seconds")
            time.sleep(5)
        except Exception, ex:
            return self.returnResult('FAIL', ex.message)
        
        return self.returnResult('PASS', '')
    
    def cleanup(self):
        self._update_carribag()