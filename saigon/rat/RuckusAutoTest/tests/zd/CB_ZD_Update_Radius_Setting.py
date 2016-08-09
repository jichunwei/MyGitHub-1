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
        
        
Create on 2012-10-26
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers

class CB_ZD_Update_Radius_Setting(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'new_cfg':{'server_name': 'radius-svr',
                                    'server_addr': '192.168.0.252',
                                    'radius_auth_secret': '1234567890',
                                    'server_port': '1812',
                                    'secondary_server_addr':'192.168.0.250',
                                    'secondary_server_port':'18120',
                                    'secondary_radius_auth_secret':'1234567890',},
                    'server_name':'radius-svr'}
        self.conf.update(conf)
        self.server_name = self.conf.get('server_name')
        self.new_cfg = self.conf.get('new_cfg')
        
        self.zd = self.testbed.components['ZoneDirector']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            Helpers.zd.aaa.edit_server(self.zd, 
                                       self.server_name, 
                                       self.new_cfg)
            return self.returnResult('PASS', 
                                     'Update AAA %s DONE' % self.server_name)
        except Exception, e:
            import traceback
            traceback.print_exc()
            return self.returnResult("FAIL", e.message)
        
    
    def cleanup(self):
        self._update_carribag()