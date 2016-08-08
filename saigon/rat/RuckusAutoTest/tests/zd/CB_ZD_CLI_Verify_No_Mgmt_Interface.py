'''
Description:

    Verify there is no Mgmt_Interface information on CLI.
    
@author: louis.lou@ruckuswireless.com
'''
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import mgmt_interface_info as cli

class CB_ZD_CLI_Verify_No_Mgmt_Interface(Test):
    '''
    
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        
        if cli.verify_no_mgmt_if_info(self.mgmt_interface_info_on_cli):
            self.passmsg = 'There is no Mgmt_Interface information'
        else:
            self.errmsg = 'There is Mgmt_Interface information [%s]' % self.mgmt_interface_info_on_cli
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        return self.returnResult('PASS', self.passmsg) 
    
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
#        self.zd = self.testbed.components['ZoneDirector']
        self.mgmt_interface_info_on_cli = self.carrierbag['mgmt_interface_info_on_cli']
        
        self.passmsg = ""
        self.errmsg = ""
        