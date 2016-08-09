'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify system IP information between SNMP get and CLI set.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp.zd import sys_snmp_info as sys_snmp


class CB_ZD_SNMP_Verify_Sys_SNMP_Info_SNMPGet_CLIGet(Test):
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_sys_snmp_info_snmp_cli_get()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.zdcli_sys_snmp_info_dict = self.carrierbag['zdcli_sys_snmp_info']
        self.snmp_sys_snmp_info_dict = self.carrierbag['snmp_sys_snmp_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):        
        self.errmsg = ''
        self.passmsg = ''

    def _verify_sys_snmp_info_snmp_cli_get(self):
        logging.info('Verify system SNMP information SNMP get and cli get')
        try:
            res_d = sys_snmp.verify_sys_snmp_info_snmp_cli(self.snmp_sys_snmp_info_dict, self.zdcli_sys_snmp_info_dict)
            
            if res_d:
                self.errmsg = 'Data between SNMP get and CLI get are different: %s' % res_d
                
            self.passmsg = 'System SNMP information are same between SNMP get and CLI get.'
            
        except Exception, ex:
            self.errmsg = ex.message