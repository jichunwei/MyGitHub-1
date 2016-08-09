'''
Created on 2010-12-8

@author: louis.lou@ruckuswireless.com
Description:
    

'''
#import os
#import re
#import time
import random

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_zd
from RuckusAutoTest.components.lib.zdcli import set_wlan


class CB_ZD_CLI_Edit_Wlan(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        set_wlan.create_wlan(self.zdcli, self.wlan_cfg)        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

     

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.wlan_cfg = self.carrierbag['edit_wlan_cfg'] 
              
        self.wlan_list = wlan_zd.get_wlan_list(self.zd)
        self.wlan_name = random.choice(self.wlan_list)
        
        self.wlan_cfg.update({'name':self.wlan_name})
            
            
    def _update_carrier_bag(self):
        self.carrierbag['wlan_name'] = self.wlan_name
        self.carrierbag['wlan_cfg'] = self.wlan_cfg