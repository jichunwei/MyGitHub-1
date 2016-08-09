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
        
        
Create on 2013-2-6
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components.lib.zdcli import configure_wlan_groups

class CB_ZD_CLI_Create_WLAN_Groups(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(wlan_group_cfg_list = [])
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.wlan_group_cfg_list = self.conf.get('wlan_group_cfg_list')
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        #@zj 20140903 ZF-8366
        configure_wlan_groups.remove_all_wlan_members_from_wlan_group(self.zdcli, 'Default')
        try:
            configure_wlan_groups.configure_wlan_groups(self.zdcli,                                                        
                                                        self.wlan_group_cfg_list)
            return self.returnResult('PASS', 'WLAN Groups configure successfully.')
        except Exception, e:            
            return self.returnResult('FAIL', e.message)
    
    def cleanup(self):
        self._update_carribag()