'''
Created on Jan 20, 2011
@author: louis.lou@ruckuswireless.com
description:

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_zd
from RuckusAutoTest.components.lib.zdcli import set_wlan
from RuckusAutoTest.components import Helper_ZD as zhlp


class CB_ZD_CLI_Verify_Wlan_Info_Between_Set_Get(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self.errmsg = set_wlan._verify_wlan_between_set_and_get(self.cli_set, self.cli_get)
        
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
                         
                         )
        
        self.conf.update(conf)
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def _retrive_carrier_bag(self):
        self.cli_set = self.carrierbag['wlan_cfg']
        self.cli_get = self.carrierbag['zdcli_wlan_info']
             
    def _update_carrier_bag(self):
        pass         