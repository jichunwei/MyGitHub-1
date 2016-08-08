'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify system information between SNMP get and SNMP set.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp.zd import sys_info


class CB_ZD_SNMP_Verify_System_Info_SNMP_Get_Set(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_sys_info_get_set()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.snmp_sys_info_dict = self.carrierbag['snmp_sys_info_dict']
        self.test_cfg_sys_info = self.carrierbag['test_cfg_sys_info']            
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''

    def _verify_sys_info_get_set(self):
        logging.info('Verify system info snmp set and snmp get')
        try:
            test_cfg_sys_info = self.test_cfg_sys_info
            
            res_d = sys_info.verify_sys_info_snmp_test_data(self.snmp_sys_info_dict, test_cfg_sys_info, True)
            
            self.errmsg = res_d
            self.passmsg = 'System information are same between SNMP get and SNMP set'
            
        except Exception, ex:
            self.errmsg = ex.message    