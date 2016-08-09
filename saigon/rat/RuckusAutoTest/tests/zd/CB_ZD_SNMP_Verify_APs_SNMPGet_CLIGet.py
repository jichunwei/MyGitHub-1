'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify wlan groups information between SNMP get and CLI get.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp.zd import aps_info


class CB_ZD_SNMP_Verify_APs_SNMPGet_CLIGet(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_aps_snmp_cli_get()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.zdcli_ap_info = self.carrierbag['all_ap_info_on_cli']
        self.snmp_ap_info = self.carrierbag['snmp_ap_info_dict']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):   
        self.conf = {}
        self.conf.update(conf)
             
        self.errmsg = ''
        self.passmsg = ''

    def _verify_aps_snmp_cli_get(self):
        logging.info('Verify aps information between SNMP get and CLI get')
        try:
            zdcli_ap_info = self.zdcli_ap_info   
            if zdcli_ap_info.has_key('AP'):
                zdcli_ap_info = zdcli_ap_info['AP']['ID']
            else:
                zdcli_ap_info = {}
                
            snmp_ap_info = self.snmp_ap_info
            
            res_d = aps_info.verify_aps_dict_snmp_cli(snmp_ap_info, zdcli_ap_info)
            
            self.errmsg = res_d
            self.passmsg = 'Aps info are same between SNMP get and CLI get'
            
        except Exception, ex:
            self.errmsg = ex.message         
    