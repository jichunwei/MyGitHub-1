'''
Description:
Created on 2010-11-5
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_basic_info as lib

class CB_ZD_CLI_Verify_System_Name(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        r, c = lib.verify_sys_name(self.gui_d, self.cli_d['Identity'])
        if r:
            self._update_carrier_bag()    
            return self.returnResult('PASS', 'Checking system name correctly')
        else:
            return self.returnResult('FAIL', c)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.gui_d = self.carrierbag['existed_sys_name']
        self.cli_d = self.carrierbag['existed_zdcli_sys_cfg_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    
