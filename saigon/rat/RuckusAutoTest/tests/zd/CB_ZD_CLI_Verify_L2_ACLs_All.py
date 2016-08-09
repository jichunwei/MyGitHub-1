'''
Description:
    Checking specify 'user' is existed.
    
Created on 2010-9-17
@author: louis.lou@ruckuswireless.com
'''
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zdcli import l2_acl_cli as cli

class CB_ZD_CLI_Verify_L2_ACLs_All(Test):
    '''
    Verify ZD CLI L2 ACL.
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        
        if cli.verify_l2acl_all(self.l2acl_data, self.acl_name_list, self.mac_list):
            self.passmsg = 'All the L2 ACLs are corrected'
        else:
            self.errmsg = 'Not all the L2 ACLs are corrected'
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        return self.returnResult('PASS', self.passmsg) 
    
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.l2acl_data = self.carrierbag['l2acl_data']
        
        if self.carrierbag.has_key('existed_acl_name_list'):
            self.acl_name_list =  self.carrierbag['existed_acl_name_list']
            
        if self.carrierbag.has_key('existed_acl_mac_list'):
            self.mac_list = self.carrierbag['existed_acl_mac_list']
            
        self.passmsg = ""
        self.errmsg = ""
        