'''
Description:
    
Created on 2010-9-17
@author: louis.lou@ruckuswireless.com
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import l2_acl_cli as cli


class CB_ZD_CLI_Show_L2_ACLs_All(Test):
    '''
    Show ZD CLI all L2 ACL.
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):  
        self.l2acl_data = cli.show_l2acl_all(self.zdcli)
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        self.passmsg = "show l2acl all return %s" ,self.l2acl_data
        
        self._update_carrier_bag()

        return self.returnResult("PASS", self.passmsg)
        
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
#        self.zdcli = create_zd_cli_by_ip_addr(**default_cfg)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.passmsg = ""
        self.errmsg = ""
    
    def _update_carrier_bag(self):
        self.carrierbag['l2acl_data'] = self.l2acl_data    