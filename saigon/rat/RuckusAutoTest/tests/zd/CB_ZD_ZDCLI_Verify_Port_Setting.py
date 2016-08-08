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
from RuckusAutoTest.components.lib.zdcli import ap_info_cli as cli_hlp

class CB_ZD_ZDCLI_Verify_Port_Setting(Test):
    required_components = []
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)        
    
    def _retrieve_carribag(self):
        self.port_setting_cli = self.carrierbag.get("existed_port_setting_cli")
        self.port_setting_gui = self.carrierbag.get("existed_port_setting_gui")
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        (res, info) = cli_hlp.verify_ap_port_config(self.port_setting_cli, self.port_setting_gui)
        if res:            
            return self.returnResult('PASS', 'Actual info equals expect info.')
        else:
            return self.returnResult('FAIL', res)
    
    def cleanup(self):
        self._update_carribag()