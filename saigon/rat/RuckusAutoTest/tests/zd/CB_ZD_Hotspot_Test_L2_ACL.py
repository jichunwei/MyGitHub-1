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

from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Hotspot_Test_L2_ACL(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',
                         wlan_cfg = None,
                         check_status_timeout = 120,                         
                         )
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.wlan_cfg = self.conf['wlan_cfg']
        self.check_status_timeout = self.conf['check_status_timeout']
    
    def _retrieve_carribag(self):
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.acl_cfg = self.carrierbag['existed_acl_cfg']
        
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        res = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_cfg, self.check_status_timeout)
        if res and not self.acl_cfg['allowed_access']:
            return self.returnResult('PASS', 'Correct Behavior, %s.' % res)
        elif res and self.acl_cfg['allowed_access']:
            return self.returnResult('PASS', 'Incorrect Behavior, %s.' % res)
        elif not res and self.acl_cfg['allowed_access']:
            return self.returnResult('PASS', 'Correct Behavior, associate successfully.')
        else:
            return self.returnResult('PASS', 'InCorrect Behavior, the result should be disconnected.')
            
    def cleanup(self):
        self._update_carribag()