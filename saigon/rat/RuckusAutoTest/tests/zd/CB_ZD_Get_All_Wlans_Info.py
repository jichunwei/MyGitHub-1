'''
Created on 2010-12-8

@author: louis.lou@ruckuswireless.com
Description:
    

'''
#import os
#import re
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_zd
from RuckusAutoTest.components.lib.zdcli import set_wlan


class CB_ZD_Get_All_Wlans_Info(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        self.wlan_name_list = wlan_zd.get_wlan_list(self.zd)
        time.sleep(5)
        self.all_wlan_info_dict = wlan_zd.get_all_wlan_conf_detail(self.zd, self.wlan_name_list)
         
        
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
#        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def _update_carrier_bag(self):
        self.carrierbag['all_wlan_info_dict'] = self.all_wlan_info_dict
        