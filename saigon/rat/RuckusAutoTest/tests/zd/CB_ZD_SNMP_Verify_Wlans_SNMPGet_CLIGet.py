'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify wlans information between SNMP get and CLI get.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp.zd import wlan_list as wlan


class CB_ZD_SNMP_Verify_Wlans_SNMPGet_CLIGet(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_wlans_snmp_cli_get()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.zdcli_wlan_info = self.carrierbag['zdcli_wlan_info']
        self.snmp_wlan_info = self.carrierbag['snmp_wlan_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):   
        self.conf = {}
        self.conf.update(conf)
             
        self.errmsg = ''
        self.passmsg = ''

    def _verify_wlans_snmp_cli_get(self):
        logging.info('Verify wlans information between SNMP get and CLI get')
        try:
            zdcli_wlan_info = self.zdcli_wlan_info   
            snmp_wlan_info = self.snmp_wlan_info
            
            res_d = wlan.verify_wlans_dict_snmp_cli(snmp_wlan_info, zdcli_wlan_info)
            
            self.errmsg = res_d
            self.passmsg = 'Wlans info are same between SNMP get and CLI get.'
            
        except Exception, ex:
            self.errmsg = ex.message         
    