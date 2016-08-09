'''
Description:
Created on 2010-11-5
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_if_info as lib

class CB_ZD_CLI_Verify_Sys_Interface_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        r, c = lib.verify_device_ip_addr(self.gui_d, self.cli_d['Device IP Address'])
        if r: 
            self._update_carrier_bag()        
            return self.returnResult('PASS', 'System interface information validate successfully')
        else:
            return self.returnResult('FAIL', c)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.gui_d = self.carrierbag['existed_ip_cfg']
        self.cli_d = self.carrierbag['existed_zdcli_sys_if_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
    
