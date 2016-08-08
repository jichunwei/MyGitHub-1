'''
Created on 2011-2-19
@author: louis.lou@ruckuswireless.com
description:

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import sys_if_info as sys_if

class CB_ZD_CLI_Verify_SYS_IF_Set_Get(Test):
    '''
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        cli_get = sys_if.get_sys_if_info(self.zdcli)
        
        self.errmsg = sys_if.verify_cli_set_get(self.sys_if_conf,cli_get)
        
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
                         sys_if_conf = dict()
                         )
        
        self.conf.update(conf)
        self.sys_if_conf = self.conf['sys_if_conf']
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass
    
            