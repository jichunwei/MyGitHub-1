'''
Created on Jan 24, 2014

@author: jacky luh
'''
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
        
'''

import logging
import traceback

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers
import lib_clean_up as rmhlp 

class CB_ZD_Clean_Up_Test_Configs(Test):
    required_components = ['ZoneDirector', 'ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            rmhlp.remove_all_cfg(self.zd, self.zdcli)
        except Exception, e:
            traceback.print_exc()
            return self.returnResult('FAIL', e.message)
        
        return self.returnResult('PASS', 'Remove all configurations DONE.')
    
    def cleanup(self):
        self._update_carribag()
