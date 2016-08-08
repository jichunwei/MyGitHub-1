'''
Description:
Created on 2010-8-5
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import (    
    create_zd_cli_by_ip_addr,
    )
from RuckusAutoTest.common import lib_Debug as bugme

class CB_Scaling_Generate_ZDCLI(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        self.zd = self.testbed.components['ZoneDirector']   
        self._gen_new_zd_cli(self.zd)           
        self._update_carrier_bag()
        
        return self.returnResult("PASS", "New CLI generate successfully")
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _gen_new_zd_cli(self, zd):
        cli = self.testbed.components['ZoneDirectorCLI']
        bugme.do_trace('cli.test')
        if cli:
            try:             
                del(cli)
            except:
                pass
            
        zdcli = create_zd_cli_by_ip_addr(ip_addr = zd.ip_addr,
                                         username = zd.username, 
                                         password = zd.password,
                                         shell_key = self.testbed.get_zd_shell_key())
        
        self.testbed.components['ZoneDirectorCLI'] = zdcli