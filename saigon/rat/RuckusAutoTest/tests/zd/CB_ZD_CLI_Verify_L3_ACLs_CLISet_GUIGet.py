'''
Created on Jan 28, 2011
@author: louis.lou@ruckuswireless.com
description:

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import l3_acl 

from RuckusAutoTest.components.lib.zd import access_control_zd as acl

class CB_ZD_CLI_Verify_L3_ACLs_CLISet_GUIGet(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        for l3acl_conf in self.l3acl_conf_list:
            gui_get = acl.get_l3_acl_policy_cfg(self.zd,l3acl_conf['acl_name'])
            logging.info('cli set is:[%s]\n gui_get is: [%s]' %(l3acl_conf,gui_get))
            self.errmsg = l3_acl._verify_l3acl_cliset_guiget(l3acl_conf, gui_get)
        
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