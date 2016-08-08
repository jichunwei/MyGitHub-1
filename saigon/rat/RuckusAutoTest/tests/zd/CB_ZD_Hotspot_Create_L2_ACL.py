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
        
        
Create on 2011-8-15
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers

class CB_ZD_Hotspot_Create_L2_ACL(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(acl_cfg = {'acl_name': 'The wireless client ACL',
                                    'allowed_access':False, 
                                    'mac_list':[]})
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.acl_cfg = self.conf['acl_cfg']
        self._retrieve_carribag()
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         self.carrierbag['existed_acl_cfg'] = self.acl_cfg
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            Helpers.zd.ac.create_l2_acl_policy(self.zd, self.acl_cfg) 
            return self.returnResult('PASS', 'L2 ACL create succesfully.')           
        except Exception, e:
            return self.returnResult('FAIL', e.message)        
    
    def cleanup(self):
        self._update_carribag()
        pass