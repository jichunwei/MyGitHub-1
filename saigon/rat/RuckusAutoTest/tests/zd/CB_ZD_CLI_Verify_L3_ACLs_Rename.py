'''
Created on Jan 28, 2011
@author: louis.lou@ruckuswireless.com
description:

'''
import random

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zdcli import l3_acl 



class CB_ZD_CLI_Verify_L3_ACLs_Rename(Test):
    '''
    Verify L3 ACL is modified name.
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        edit_l3acl_conf = random.choice(self.l3acl_conf_list)
        edit_l3acl_conf.update(dict(new_name = 'new-name' + utils.make_random_string(random.randint(2,24),type = 'alnum')))
        l3_acl._rename_l3acl(self.zdcli, edit_l3acl_conf)  
        
        cli_get = l3_acl.show_l3acl_name(self.zdcli, edit_l3acl_conf['new_name'])
        
        if cli_get['Name'] != edit_l3acl_conf['new_name']:
            self.errmsg = "L3 ACL name not renamed"
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

     

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         l3acl_conf_list = conf['l3acl_conf_list']
                         )
        
        self.conf.update(conf)
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.l3acl_conf_list = self.conf['l3acl_conf_list']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         