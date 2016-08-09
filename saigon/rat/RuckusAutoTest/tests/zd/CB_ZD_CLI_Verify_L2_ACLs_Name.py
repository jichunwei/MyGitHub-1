'''
Description:
    
Created on 2010-9-17
@author: louis.lou@ruckuswireless.com
'''
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import l2_acl_cli as cli


class CB_ZD_CLI_Verify_L2_ACLs_Name(Test):
    '''
    Show ZD CLI L2 ACL by name.
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):
        for l2acl_name in self.acl_name_list:
            self.l2acl_data = cli.show_l2acl_name(self.zdcli, l2acl_name)
            if cli.verify_l2acl_name(self.l2acl_data, l2acl_name, self.mac_list):
                self.passmsg = "All the CLI show l2acl name $name are corrected"
            else:
                self.errmsg = 'Not all the show l2acl name $name are correct'
                
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult("PASS", self.passmsg)
        
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        if self.carrierbag.has_key('existed_acl_name_list'):
            self.acl_name_list =  self.carrierbag['existed_acl_name_list']
            
        if self.carrierbag.has_key('existed_acl_mac_list'):
            self.mac_list = self.carrierbag['existed_acl_mac_list']
            
        self.passmsg = ""
        self.errmsg = ""
       
    def _update_carrier_bag(self):
        self.carrierbag['l2acl_data'] = self.l2acl_data      