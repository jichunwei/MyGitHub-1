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
        
        
Create on 2012-5-29
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers

class CB_ZD_Set_Northbound_Interface(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(enable = True,
                         password = "1234",
                         )
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.enable = self.conf['enable']
        self.password = self.conf['password']
        
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            if self.enable:
                Helpers.zd.nb.enable(self.zd, self.password)
            else:
                Helpers.zd.nb.disable(self.zd)
            return self.returnResult('PASS', 'Set Northbound Interface as %s' % self.enable)
        
        except Exception, e:                        
            return self.returnResult('FAIL', e.message)
    
    def cleanup(self):
        self._update_carribag()