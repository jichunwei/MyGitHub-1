'''
Description:
Created on 2010-11-4
@author: cwang@ruckuswireless.com
'''
import copy

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_snmp_info as lib

class CB_ZD_CLI_Verify_SNMP_Trap_Info(Test):
    '''
    '''
    required_components = ['ZoneDirectorCLI']
    parameter_description = {}
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        cli_d = copy.deepcopy(self.cli_d)
        gui_d = copy.deepcopy(self.gui_d)
        if not gui_d['enabled']:
            for key in gui_d.keys():
                if key != 'enabled':
                    gui_d.pop(key)
            for key in cli_d.keys():
                if key != 'Status':
                    cli_d.pop(key)
        
        r, c = lib.verify_snmp_trap(gui_d, cli_d)
        if r:
            self._update_carrier_bag()
            return self.returnResult('PASS', 'SNMP Trap checking successfully')
        else:
            return self.returnResult('FAIL', c)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.gui_d = self.carrierbag['existed_snmp_trap_info']
        self.cli_d = self.carrierbag['zdcli_sys_snmp_trap_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.errmsg = ''
        self.passmsg = ''
    
