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
       - Resolve AP Group port setting.
   2. Test:
       - Navigate to AP Group configuration page
       - Update AP Group port setting against AP model.
       - Get/Verify the Setting is correct as expected.
   3. Cleanup:
       - 
    How it was tested:
        
        
Create on 2012-10-12
@author: cwang@ruckuswireless.com
'''

import logging
import traceback

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import ZoneDirector

from RuckusAutoTest.components import Helpers

class CB_ZD_Configure_AP_Group_Port_Config(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def _init_params(self, conf):
        """
            Configuration sample:
            {'group_name':'mytest',
            'port_setting':{'zf7962':{'lan1':{
                        'enabled': True,
                        'dhcp82': False,
                        'type': 'trunk',              #[trunk, access, general]
                        'untagged_vlan': '1',         #[1-4094, none] (expected String type)
                        'vlan_members': '1-4094',   #[1-4094] (expected String type)
                        'dot1x': 'disabled', #[disabled, supp, auth-port, auth-mac]                     
                    },
                    'lan2':{
                        'enabled': True,
                        'dhcp82': False,
                        'type': 'access',              #[trunk, access, general]
                        'untagged_vlan': '1',         #[1-4094, none] (expected String type)
#                        'vlan_members': '1-4094',   #[1-4094] (expected String type)
                        'dot1x': 'auth-mac', #[disabled, supp, auth-port, auth-mac]
                        'enable_dvlan':True,
                        'guest_vlan':'10'                        
                    }
                    }
                }
            }
        """
        self.conf = {}
        self.conf.update(conf)
        self.group_name = self.conf['group_name']
        self.port_setting = self.conf['port_setting']
        logging.info('Resolve configuration successfully.')
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
            for model, port_config in self.port_setting.items():
                Helpers.zd.apg.set_ap_port_config_by_ap_model(self.zd, 
                                                              self.group_name, 
                                                              model, port_config)
            return self.returnResult('PASS', 
                                     'Port Setting on ap group %s is done' % self.group_name)
            
        except Exception, e:
            logging.error(traceback.format_exc())
            return self.returnResult('FAIL', e.message)
                    
    
    def cleanup(self):
        self._update_carribag()