'''
Description:Checking Admin info between GUI and CLI.
Created on 2010-10-26
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import admin as lib

class CB_ZD_CLI_Verify_Admin_Info(Test):
    '''
     Checking Admin info between GUI and CLI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self.gui_d = self.zd.get_admin_cfg()
        r, c = lib.verify_admin_info(self.gui_d, self.zdcli_admin_info)
        if r:            
            return self.returnResult('PASS', 'Admin [%s] checking between GUI and CLI is correct' % self.zdcli_admin_info)
        else:
            return self.returnResult('FAIL', c)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.zdcli_admin_info = self.carrierbag['zdcli_admin_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.passmsg = ''
    
