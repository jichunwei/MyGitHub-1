'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify system information between SNMP get and CLI set.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp.zd import sys_info


class CB_ZD_SNMP_Verify_System_Info_SNMPGet_CLIGet(Test):
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_sys_info_snmp_cli_get()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.zdcli_sys_info_dict = self.carrierbag['zdcli_sys_info_dict']
        self.snmp_sys_info_dict = self.carrierbag['snmp_sys_info_dict']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):        
        self.errmsg = ''
        self.passmsg = ''

    def _verify_sys_info_snmp_cli_get(self):
        logging.info('Verify system information SNMP get and CLI get')
        try:
            res_d = sys_info.verify_sys_info_snmp_cli(self.snmp_sys_info_dict, self.zdcli_sys_info_dict, True, True)
            
            self.errmsg = res_d
            self.passmsg = 'System information are same between SNMP get and CLI get.'
            
        except Exception, ex:
            self.errmsg = ex.message