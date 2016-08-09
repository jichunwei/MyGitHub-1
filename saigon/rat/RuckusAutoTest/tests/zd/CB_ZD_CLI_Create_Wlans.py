'''
Created on 2010-12-6

@author: louis.lou@ruckuswireless.com
Description:
    Create Wlan list

'''
#import os
#import re
#import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_zd
from RuckusAutoTest.components.lib.zdcli import set_wlan


class CB_ZD_CLI_Create_Wlans(Test):
    '''
    Create  Wlan List via CLI
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        self.errmsg = set_wlan.create_multi_wlans(self.zdcli, self.wlan_conf_list)  
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        self.passmsg = 'Create WLAN Successfully'
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

     

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = dict(
                         wlan_cfg_list =[],
                         )
        
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('wlan_cfg_list'):
            self.wlan_conf_list = self.conf['wlan_cfg_list']            
        elif self.carrierbag.get('wlan_cfg_list'):
            self.wlan_conf_list = self.carrierbag['wlan_cfg_list']
        else:
            raise Exception("Please provide wlan_cfg_list")

    def _update_carrier_bag(self):
        #@author: chen.tao since 2014-10-21, to fix ZF-10167
        for wlan_cfg in self.wlan_conf_list:
            if wlan_cfg.get('name'):
                self.carrierbag[wlan_cfg['name']] = wlan_cfg
            if wlan_cfg.get('ssid'):
                self.carrierbag[wlan_cfg['ssid']] = wlan_cfg            
            self.carrierbag['wlan_conf_list'] = self.wlan_conf_list
            

