'''
Description:Checking system usage summary between GUI and CLI.
Created on 2010-10-26
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_basic_info  as lib

class CB_ZD_CLI_Verify_Usage_Summary(Test):
    '''
     Checking usage summary between GUI and CLI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):            
        pass_msg_list = []    
        r, c = lib.verify_usage_summary(self.gui_sys_usage_summary, self.cli_sys_info['Usage Summary'], lib.HOUR)        
        if r:            
            pass_msg_list.append('Usage of 1 hour checking is correct')
        else:
            return self.returnResult('FAIL', c)
        
        r, c = lib.verify_usage_summary(self.gui_sys_usage_summary, self.cli_sys_info['Usage Summary'], lib.DAY)        
        if r:            
            pass_msg_list.append('Usage of 1 day checking is correct')
        else:
            return self.returnResult('FAIL', c)
        
        return self.returnResult('PASS', pass_msg_list)
        
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.gui_sys_usage_summary = self.carrierbag['existed_sys_usage_summary']
        self.cli_sys_info = self.carrierbag['existed_zdcli_sys_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)        
        self.errmsg = ''
        self.passmsg = ''
    
