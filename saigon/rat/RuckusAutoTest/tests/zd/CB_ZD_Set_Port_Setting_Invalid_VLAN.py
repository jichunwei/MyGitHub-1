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
        
        
Create on 2012-10-25
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components import Helpers

class CB_ZD_Set_Port_Setting_Invalid_VLAN(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'ap_mac_addr':None,
                     'port_setting': None,}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.ap_mac_addr = self.conf.get('ap_mac_addr')
        self.port_setting = self.conf.get('port_setting')
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
#        gvlan = self.port_setting['guest_vlan']
        try:
            Helpers.zd.ap.set_ap_port_config_by_mac(self.zd, 
                                                    self.ap_mac_addr, 
                                                    self.port_setting)
            
            return self.returnResult("FAIL", 
                                     "Incorrect Behavior, \
                                     should raise exception \
                                     when set guest vlan out of [1, 4094]")
        except Exception, e:            
            if 'Can not set value' in e.message:
                return self.returnResult("PASS", "Correct Behavior, %s" % e.message)    
        
    
    def cleanup(self):
        self._update_carribag()