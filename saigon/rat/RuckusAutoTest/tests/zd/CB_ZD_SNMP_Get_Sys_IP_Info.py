'''
Created on Apr 09, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to get system IP information via ZD SNMP.
'''

import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import sys_ip_info as sys_ip

class CB_ZD_SNMP_Get_Sys_IP_Info(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_system_ip_info()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag() 
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _get_system_ip_info(self):
        try:
            logging.info('Get system IP information via ZD SNMP.')
                     
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))
                           
            snmp = helper.create_snmp(snmp_cfg)
            
            sys_ip_info_d = sys_ip.get_sys_ip_info(snmp)
            self.snmp_sys_ip_info_dict = sys_ip_info_d
            
            logging.info('SNMP system IP information: %s' % self.snmp_sys_ip_info_dict)
            self.passmsg = 'Get system IP information via ZD SNMP successfully.'
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['snmp_sys_ip_info'] = self.snmp_sys_ip_info_dict
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                
        self.errmsg = ''
        self.passmsg = ''
