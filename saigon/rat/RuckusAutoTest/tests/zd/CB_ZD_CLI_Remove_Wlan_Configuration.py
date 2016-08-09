'''
Created on 2010-12-29

@author: louis.lou@ruckuswireless.com
Description:
    

'''
#import os
#import re
#import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_zd
from RuckusAutoTest.components.lib.zdcli import set_wlan


class CB_ZD_CLI_Remove_Wlan_Configuration(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
       
        self.errmsg = set_wlan.remove_wlan_config(self.zdcli,self.wlan_name)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

     

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = dict(
                         
                         )
        
        self.conf.update(conf)
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.wlan_name = self.carrierbag['wlan_name']
    def _update_carrier_bag(self):
        pass