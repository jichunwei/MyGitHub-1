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

class CB_ZD_Hotspot_Config_L2_ACL(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(sta_tag = 'sta_1',
                         acl_cfg = {'acl_name': 'The wireless client ACL',
                                    'allowed_access':False, 
                                    'mac_list':[]},
                         )
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self._retrieve_carribag()
    
    
    def _retrieve_carribag(self):
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        if (self.conf['acl_cfg'] and not self.conf['acl_cfg']['mac_list']):
            self.wifi_mac_addr = self.carrierbag.get(self.conf['sta_tag'])['wifi_mac_addr']
            self.wifi_ip_addr = self.carrierbag.get(self.conf['sta_tag'])['wifi_ip_addr']
            self.conf['acl_cfg']['mac_list'] = [self.wifi_mac_addr]
        self.existed_acl_cfg = self.carrierbag['existed_acl_cfg']
               
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            Helpers.zd.ac.edit_l2_acl_policy(self.zd, 
                                         self.existed_acl_cfg['acl_name'], 
                                         self.conf['acl_cfg'])
        except Exception, e:
            return self.returnResult('FAIL', e.message)
        
        return self.returnResult('PASS', 'ACL configure successfully.')
    
    def cleanup(self):
        self._update_carribag()