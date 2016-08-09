'''
Created on Oct 30, 2013
@author: lab
'''
'''        
Create on 2013-10-30
@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components.lib.zdcli import configure_wlan_groups

class CB_ZD_CLI_Set_Default_WLAN_Groups(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = {'wg_name': 'Default', 
                     'description': '',
                     'wlan_member': {}}
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.cfg = {'wg_name': 'Default', 
                     'description': '',
                     'wlan_member': {}}
        for key, value in self.conf.items():
            if self.cfg.has_key(key):
                self.cfg[key]=value
        
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            configure_wlan_groups.configure_wlan_groups(self.zdcli,                                                        
                                                        [self.cfg])
            
            return self.returnResult('PASS', 'WLAN Groups configure successfully.')
        except Exception, e:            
            return self.returnResult('FAIL', e.message)
    
    def cleanup(self):
        self._update_carribag()