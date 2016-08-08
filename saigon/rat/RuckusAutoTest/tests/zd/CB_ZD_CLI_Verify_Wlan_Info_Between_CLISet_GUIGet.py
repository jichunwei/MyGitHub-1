'''
Created on Jan 20, 2011
@author: louis.lou@ruckuswireless.com
description:

'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import set_wlan


class CB_ZD_CLI_Verify_Wlan_Info_Between_CLISet_GUIGet(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self.errmsg = set_wlan._verify_wlan_between_cli_set_and_gui_get(self.cli_set, self.gui_get)
        
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
        
    def  _retrive_carrier_bag(self):
        self.cli_set = self.carrierbag['wlan_cfg']
        self.gui_get = self.carrierbag['wlan_info_gui_get']
             
    def _update_carrier_bag(self):
        pass         