'''
Description:Call show sys command from CLI.
Created on 2010-11-3
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_basic_info  as lib

class CB_ZD_CLI_Get_System_Info(Test):
    '''
    Get system info from CLI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):                
        self.sys_info = lib.get_sys_info(self.zdcli)
        self._update_carrier_bag()
        return self.returnResult('PASS', 'Command show sys work well')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_zdcli_sys_info'] = self.sys_info
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    
