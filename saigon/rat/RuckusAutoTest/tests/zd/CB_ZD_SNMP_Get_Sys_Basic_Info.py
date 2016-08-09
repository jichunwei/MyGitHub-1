'''
Created on Mar 27, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to get system information via ZD SNMP.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import sys_info

class CB_ZD_SNMP_Get_Sys_Basic_Info(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_system_info()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _get_system_info(self):
        try:
            logging.info('Get system information via ZD SNMP.')
                     
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))                           
            snmp = helper.create_snmp(snmp_cfg)
                        
            sys_info_d = sys_info.get_sys_info(snmp)            
            self.snmp_sys_info = sys_info_d
            
            logging.info('SNMP system basic information: %s' % self.snmp_sys_info)
            self.passmsg = 'Get system basic information via ZD SNMP successfully.'
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['snmp_sys_info'] = self.snmp_sys_info
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                
        self.errmsg = ''
        self.passmsg = ''