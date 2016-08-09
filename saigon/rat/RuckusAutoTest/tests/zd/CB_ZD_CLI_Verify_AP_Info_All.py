'''
Description:
    Checking specify 'user' is existed.
    
Created on 2010-9-26
@author: louis.lou@ruckuswireless.com
'''
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import ap_info_cli as cli

class CB_ZD_CLI_Verify_AP_Info_All(Test):
    '''
    Verify ZD CLI : show ap all.
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        
        if cli.verify_ap_all(self.all_ap_info_on_cli, self.all_ap_info_on_zd):
            self.passmsg = 'All the AP information are corrected'
        else:
            self.errmsg = 'Not all the AP information are corrected'
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        return self.returnResult('PASS', self.passmsg) 
    
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.all_ap_info_on_cli = self.carrierbag['all_ap_info_on_cli']
        self.all_ap_info_on_zd = self.carrierbag['all_ap_info_on_zd']
        
        self.passmsg = ""
        self.errmsg = ""
        