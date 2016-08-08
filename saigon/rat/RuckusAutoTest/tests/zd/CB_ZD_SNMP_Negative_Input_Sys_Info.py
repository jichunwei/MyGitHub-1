'''
Created on Mar 27, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to configure system info via zd snmp.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import sys_info
from RuckusAutoTest.components.lib.snmp.zd import sys_snmp_info

class CB_ZD_SNMP_Negative_Input_Sys_Info(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._verify_negative_input_sys_info()        
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass

    def _verify_negative_input_sys_info(self):
        logging.info('Verify negative input for system basic and snmp info.')
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))               
            snmp = helper.create_snmp(snmp_cfg)
            
            res_d = {}
            
            sys_basic_info_cfg = sys_info.gen_test_data_sys_info_negative()        
            res_sys_basic_d = sys_info.update_sys_info(snmp, sys_basic_info_cfg)            
            res_d.update(res_sys_basic_d)
            
            sys_snmp_info_cfg = sys_snmp_info.gen_test_data_sys_snmp_info_negative()
            res_sys_snmp_d = sys_snmp_info.set_sys_snmp_info(snmp, sys_snmp_info_cfg, [], False)
            res_d.update(res_sys_snmp_d)
            
            pass_d, fail_d = helper.verify_error_for_negative(res_d)
        
            if pass_d:
                logging.info('Pass information: %s' % pass_d)
            if fail_d:
                logging.warning('Error:' % fail_d)
                self.errmsg = fail_d
            else:                
                self.passmsg = 'Error message is correct for negative input.'            
                                    
        except Exception, ex:
            self.errmsg = ex.message