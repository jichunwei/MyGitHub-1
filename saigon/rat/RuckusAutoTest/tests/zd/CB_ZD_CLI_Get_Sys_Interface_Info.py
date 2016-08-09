'''
Description:
Created on 2010-11-5
@author: cwang@ruckuswireless.com
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_if_info as lib

class CB_ZD_CLI_Get_Sys_Interface_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        self.sys_if_info = lib.get_sys_if_info(self.zdcli)
        self._update_carrier_bag()        
        return self.returnResult('PASS', 'Get system interface information from CLI successfully')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_zdcli_sys_if_info'] = self.sys_if_info 
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    
