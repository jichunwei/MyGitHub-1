'''
Description:
    1) Go to config.
    2) Enter system.
    3) show.
Created on 2010-11-4
@author: cwang@ruckuswireless.com
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_basic_info as lib

class CB_ZD_CLI_Get_Cfg_Sys_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):                
        self.zdcli_sys_cfg_info = lib.get_cfg_sys_info(self.zdcli)
        self._update_carrier_bag()
        return self.returnResult('PASS', 'Get system configuration info from ZDCLI successfully')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_zdcli_sys_cfg_info'] = self.zdcli_sys_cfg_info
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    
