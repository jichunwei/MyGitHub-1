'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
       Negative scenarios:
           300, Not found:  Wrong macaddr or ipaddr
           302, Bad request:XML request is not well-formed
           303, Version not support, version mismatch
           400, Internal server error, ZD internal error
           401, Radius server error, RADIUS connection error or timeout               

   Required components: 
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
        
        
Create on 2012-5-29
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers

class CB_WebPortal_User_Authentication_Negative_Test(Test):
    required_components = []
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',                         
                         )
        self.conf.update(conf)        
        self.sta_tag = self.conf['sta_1']
        
    
    def _retrieve_carribag(self):
        self.ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        self.mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        self.kwargs['ipaddr'] = self.ip_addr
        self.kwargs['macaddr'] = self.mac_addr
    
    def test(self):        
        #To-do            
        if code == self.expected_code:
            return self.returnResult('PASS', msg)
        else:
            return self.returnResult('FAIL', 
                                     'Expected code %s, actual code %s' % \
                                     (self.expected_code, code))
        
    
    def cleanup(self):
        self._update_carribag()
    