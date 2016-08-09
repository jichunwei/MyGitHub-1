'''
Description:
Created on 2010-11-4
@author: cwang@ruckuswireless.com
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_snmp_info as lib

class CB_ZD_CLI_Verify_SNMPV2_Info(Test):
    '''
    '''
    required_components = ['ZoneDirectorCLI']
    parameter_description = {}
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        r, c = lib.verify_snmpv2_agent(self.gui_d, self.cli_d)
        if r:
            self._update_carrier_bag()        
            return self.returnResult('PASS', 'SNMPV2 agent info is the same between GUI and CLI.')
        else:
            return self.returnResult('FAIL', c)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.gui_d = self.carrierbag['existed_snmp_agent_info']
        self.cli_d = self.carrierbag['existed_zdcli_sys_snmpv2_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)            
        self.errmsg = ''
        self.passmsg = ''