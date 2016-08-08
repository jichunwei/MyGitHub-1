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
from RuckusAutoTest.components import ZoneDirector
from RuckusAutoTest.components.lib.zdcli import configure_ap as aphlp

class CB_ZDCLI_Set_Port_Setting(Test):
    required_components = ['ZoneDirectorCLI']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(port_setting = {'override_parent': True,
                                         'lan2': {
                                                 'enabled': True,
                                                 'type': 'trunk',              #[trunk, access, general]
                                                 'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                                                 'vlan_members': '1-4094',   #[1-4094] (expected String type)
                                                 'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]
                                              },
                                        },
                        ap_mac_addr = None,#Mac Addr
                                        )
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.mac_addr = self.conf['ap_mac_addr']
        self.port_setting = self.conf['port_setting']
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:
            res, msg  = aphlp.set_ap_port_config_by_mac(self.zdcli, self.mac_addr, self.port_setting)
            if res:
                return self.returnResult('PASS', 'AP %s configure successfully' % self.mac_addr)
            else:
                return self.returnResult("FAIL", msg)
            
        except Exception, e:
            return self.returnResult("FAIL", e.message)
        
    
    def cleanup(self):
        self._update_carribag()