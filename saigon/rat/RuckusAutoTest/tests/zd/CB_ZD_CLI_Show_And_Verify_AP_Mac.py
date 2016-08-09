'''
Description:
    
Created on 2010-9-26
@author: louis.lou@ruckuswireless.com
'''

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import ap_info_cli as cli


class CB_ZD_CLI_Show_And_Verify_AP_Mac(Test):
    '''
    ZD CLI: Show AP mac $mac.
    Verify the show message is correct.
    '''
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):  
        logging.info('Show ap devname $name')
        for mac in self.mac_list:
            ap_info_on_cli = cli.show_ap_info_by_mac(self.zdcli, mac) 
            k = ap_info_on_cli['AP']['ID'].keys()[0]
            ap_info_on_zd = self.zd.get_ap_info_ex(mac)
            cli.verify_ap_mac(ap_info_on_cli, ap_info_on_zd,k)
            
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        self.passmsg = "The command: show ap mac $mac correct"
        
        self._update_carrier_bag()

        return self.returnResult("PASS", self.passmsg)
        
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.mac_list = self.carrierbag['mac_list']
#        self.all_ap_info_on_cli = self.carrierbag['all_ap_info_on_cli']
        
        self.passmsg = ""
        self.errmsg = ""
    
    def _update_carrier_bag(self):
#        self.carrierbag['all_ap_info_on_cli'] = self.all_ap_info_on_cli    
        pass