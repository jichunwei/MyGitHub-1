'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description:
    This script is to get snmp agent v3 information from GUI.
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Get_SNMP_Agent_V3_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        self.snmp_agent_info = lib.zd.sys.get_snmp_agent_v3_info(self.zd)
        self._update_carrier_bag()        
        return self.returnResult('PASS', 'Get SNMP Agent V3 Info successfully: %s' % self.snmp_agent_info)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_snmp_agent_v3_info'] = self.snmp_agent_info
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
