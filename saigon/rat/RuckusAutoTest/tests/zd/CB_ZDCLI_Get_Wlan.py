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
        
        
Create on 2012-2-20
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi

class CB_ZDCLI_Get_Wlan(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(ssid = None)
        self.conf.update(conf)
        self.ssid = self.conf['ssid']        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ""
        self.passmsg = ""
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         self.carrierbag['existed_zdcli_wlan'] = self.wlan_info
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        self._get_wlan_info()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        self._update_carribag()
        return self.returnResult('PASS', self.passmsg)
    
    def _get_wlan_info(self):
        try:
            self.wlan_info = gwi.get_wlan_by_ssid(self.zdcli, self.ssid)            
        except Exception, ex:
            self.errmsg = ex.message
            
        self.passmsg = 'Get WLAN information by SSID from zd cli successfully'
    
    def cleanup(self):
        self._update_carribag()