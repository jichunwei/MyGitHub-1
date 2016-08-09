'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify wlan groups information between SNMP get and CLI get.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp.zd import wlan_group_list as wlangroup


class CB_ZD_SNMP_Verify_Wlan_Groups_SNMPGet_CLIGet(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_wlan_groups_snmp_cli_get()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.zdcli_wlan_group_info = self.carrierbag['zdcli_all_wlan_group']
        self.snmp_wlan_group_info = self.carrierbag['snmp_wlan_group_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):   
        self.conf = {}
        self.conf.update(conf)
             
        self.errmsg = ''
        self.passmsg = ''

    def _verify_wlan_groups_snmp_cli_get(self):
        logging.info('Verify wlan groups information between SNMP get and CLI get')
        try:
            zdcli_wlan_group_info = self.zdcli_wlan_group_info   
            snmp_wlan_group_info = self.snmp_wlan_group_info
            
            res_d = wlangroup.verify_wlan_groups_snmp_cli(snmp_wlan_group_info, zdcli_wlan_group_info)
            
            self.errmsg = res_d
            self.passmsg = 'Wlan groups info are same between SNMP get and CLI get.'
            
        except Exception, ex:
            self.errmsg = ex.message         
    