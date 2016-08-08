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
        
        
Create on 2012-2-15
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import set_wlan as hlp

class CB_ZD_CLI_Configure_WLAN(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(wlan_cfg = None)
        self.conf.update(conf)
        self.wlan_cfg = self.conf['wlan_cfg']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            hlp.create_wlan(self.zdcli, self.wlan_cfg)
        except Exception, ex:
            self.errmsg = ex.message

        if self.errmsg:
            if self.conf.get('negative'):
                return self.returnResult("PASS", self.errmsg)
            else:
                return self.returnResult("FAIL", self.errmsg)
        else:
            self.passmsg = 'Create WLAN from CLI successfully.'
            if self.conf.get('negative'):
                return self.returnResult("FAIL", self.passmsg)
            else:
                return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        self._update_carribag()
        