'''
Description:

    Verify the SR information on CLI is the same as ZD GUI.
    
@author: louis.lou@ruckuswireless.com
'''
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import smart_redundancy_info as cli

import logging

class CB_ZD_CLI_Verify_SR_Info(Test):
    '''
    Verify ZD CLI : Smart Redundancy information
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        logging.info('cli_info is:%s, web_info is:%s' % (self.sr_info_on_cli, self.sr_info_on_zd))
        if cli.verify_sr_info(self.sr_info_on_cli, self.sr_info_on_zd):
            self.passmsg = 'All the SR information are corrected'
        else:
            self.errmsg = 'Not all the SR information are corrected, cli_info is:%s, web_info is:%s' % (self.sr_info_on_cli, self.sr_info_on_zd)
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        return self.returnResult('PASS', self.passmsg) 
    
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
#        self.zd = self.testbed.components['ZoneDirector']
        self.sr_info_on_cli = self.carrierbag['sr_info_on_cli']
        self.sr_info_on_zd = self.carrierbag['sr_info_on_zd']
        
        self.passmsg = ""
        self.errmsg = ""
        