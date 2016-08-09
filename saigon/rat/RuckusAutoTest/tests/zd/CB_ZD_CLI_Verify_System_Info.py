'''
Description:Checking system info between GUI and CLI.
Created on 2010-10-26
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_basic_info  as lib

class CB_ZD_CLI_Verify_System_Info(Test):
    '''
     Checking system info between GUI and CLI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):                    
        r, c = lib.verify_sys_overview(self.gui_sys_info, self.cli_sys_info['System Overview'])        
        if r:            
            return self.returnResult('PASS', 'System overview checking between GUI and CLI is correct')
        else:
            return self.returnResult('FAIL', c)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.gui_sys_info = self.carrierbag['existed_sys_info']
        self.cli_sys_info = self.carrierbag['existed_zdcli_sys_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)        
        self.errmsg = ''
        self.passmsg = ''
    
