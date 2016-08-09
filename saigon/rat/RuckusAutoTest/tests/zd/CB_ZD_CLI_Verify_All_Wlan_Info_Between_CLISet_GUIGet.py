'''
Created on 2010-12-8

@author: louis.lou@ruckuswireless.com
Description:
    

'''
#import os
#import re
#import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_zd
from RuckusAutoTest.components.lib.zdcli import set_wlan


class CB_ZD_CLI_Verify_All_Wlan_Info_Between_CLISet_GUIGet(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        try:
            if not self.gui_get_dict:
                wlan_name_list = wlan_zd.get_wlan_list(self.zd)
                self.gui_get_dict = wlan_zd.get_all_wlan_conf_detail(self.zd, wlan_name_list)
        
            self.errmsg = set_wlan.verify_wlan_between_cli_set_and_gui_get(self.cli_set_list, self.gui_get_dict)
       
        except Exception, ex:
            self.errmsg = ex.message
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        
        self.passmsg = 'Wlan info are the same between CLI Set and GUI Get'
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
        
        if self.carrierbag.has_key('all_wlan_info_dict'):
            self.gui_get_dict = self.carrierbag['all_wlan_info_dict']
        
        else:
            self.gui_get_dict = {}
            
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
    def _update_carrier_bag(self):
        pass