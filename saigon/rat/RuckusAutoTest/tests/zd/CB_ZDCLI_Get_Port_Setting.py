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
        
        
Create on 2012-3-19
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import ap_info_cli as aphlp

class CB_ZDCLI_Get_Port_Setting(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(ap_mac_addr = None)
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.ap_mac_addr = self.conf['ap_mac_addr']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         self.carrierbag['existed_port_setting_cli'] = self.port_setting
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            self.port_setting = aphlp.show_ap_port_config_by_mac(self.zdcli, self.ap_mac_addr)
            self._update_carribag()
            return self.returnResult("PASS", "Get OK.")
        except Exception, e:                    
            return self.returnResult('FAIL', e.message)
    
    def cleanup(self):
        pass