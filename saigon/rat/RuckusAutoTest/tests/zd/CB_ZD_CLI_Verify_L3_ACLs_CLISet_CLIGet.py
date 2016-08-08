'''
Created on Jan 28, 2011
@author: louis.lou@ruckuswireless.com
description:

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import l3_acl 

from RuckusAutoTest.components import Helper_ZD as zhlp


class CB_ZD_CLI_Verify_L3_ACLs_CLISet_CLIGet(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        for l3acl_conf in self.l3acl_conf_list:
            cli_get = l3_acl.show_l3acl_name(self.zdcli, l3acl_conf['acl_name'])
            logging.info('cli set is:[%s]\n cli_get is: [%s]' %(l3acl_conf,cli_get))
            logging.info('Verify L3 ACL set and get are the same')
            self.errmsg = l3_acl._verify_l3acl_cliset_cliget(l3acl_conf, cli_get)
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
                         l3acl_conf_list = []
                         )
        
        self.conf.update(conf)
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.l3acl_conf_list = self.conf['l3acl_conf_list']  
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         