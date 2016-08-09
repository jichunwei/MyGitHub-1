'''
Created on 2010-12-8

@author: louis.lou@ruckuswireless.com
Description:
    

'''
#import os
#import re
#import time
#import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.lib.zd import wlan_zd
from RuckusAutoTest.components.lib.zdcli import set_wlan
from RuckusAutoTest.components.lib.zdcli import get_wlan_info as gwi


class CB_ZD_CLI_Verify_All_Wlan_Info_Between_Set_Get(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        try:
            if not self.cli_get_dict:
                self.cli_get_dict = gwi.get_wlan_all(self.zdcli)
            
            self.errmsg = set_wlan.verify_wlan_all_between_set_and_get(self.cli_set_list, self.cli_get_dict)
            
        except Exception, ex:
            self.errmsg = ex.message
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        self.passmsg = 'Wlan info are the same between CLI Set and CLI Get'
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = {'cli_set_list': [],
                     }
        self.conf.update(conf)
        
        self.cli_set_list = self.conf['cli_set_list']
        if not self.cli_set_list:
            self.cli_set_list = self.carrierbag['wlan_cfg_list']
        
        if self.carrierbag.has_key('zdcli_wlan_info'):
            self.cli_get_dict = self.carrierbag['zdcli_wlan_info']
        
        else:
            self.cli_get_dict = {}
            
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def _update_carrier_bag(self):
        pass