'''
Description:

    Verify there is no SR information on CLI.
    
@author: louis.lou@ruckuswireless.com
'''
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import smart_redundancy_info as cli

class CB_ZD_CLI_Verify_No_SR_Info(Test):
    '''
    
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        
        if cli.verify_no_sr_info(self.sr_info_on_cli):
            self.passmsg = 'There is no Smart Redundancy information'
        else:
            self.errmsg = 'There is Smart Redundancy information [%s]' %self.sr_info_on_cli
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        return self.returnResult('PASS', self.passmsg) 
    
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
#        self.zd = self.testbed.components['ZoneDirector']
        self.sr_info_on_cli = self.carrierbag['sr_info_on_cli']
        
        self.passmsg = ""
        self.errmsg = ""
        