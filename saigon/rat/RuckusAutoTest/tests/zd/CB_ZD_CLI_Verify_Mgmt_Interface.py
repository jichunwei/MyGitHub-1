'''
Description:

    Verify the information on CLI is the same as ZD GUI.
    
Created on 2010-10-20
@author: louis.lou@ruckuswireless.com
'''
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import mgmt_interface_info as cli
from RuckusAutoTest.components.lib.zd import mgmt_interface as mgmt

class CB_ZD_CLI_Verify_Mgmt_Interface(Test):
    '''
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        
        if cli.verify_mgmt_if_info(self.mgmt_interface_info_on_cli, self.mgmt_if_info_zd):
            self.passmsg = 'All the station information are corrected'
        else:
            self.errmsg = 'Not all the station information are corrected'
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        return self.returnResult('PASS', self.passmsg) 
    
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.mgmt_interface_info_on_cli = self.carrierbag['mgmt_interface_info_on_cli']
        if self.carrierbag.has_key('mgmt_if_info_zd'):
            self.mgmt_if_info_zd = self.carrierbag['mgmt_if_info_zd']
        else:
            self.mgmt_if_info_zd = mgmt.get_mgmt_inf(self.zd)
        
        self.passmsg = ""
        self.errmsg = ""
        