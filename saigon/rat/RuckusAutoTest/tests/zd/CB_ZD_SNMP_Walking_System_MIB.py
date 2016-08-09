'''
Created on Mar 27, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to configure system info via zd snmp.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import walking_mib as walking

class CB_ZD_SNMP_Walking_System_MIB(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._walking_system_mib()        
        
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
        self.carrierbag['snmp_sys_info'] = self.sys_info_d
        self.carrierbag['snmp_sys_ip_info'] = self.sys_ip_info_d
        self.carrierbag['snmp_sys_snmp_info'] = self.sys_snmp_info_d

    def _walking_system_mib(self):
        logging.info('Walking system mib and parsing the information')
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))               
            snmp = helper.create_snmp(snmp_cfg)
            
            all_sys_info_d = walking.walking_system_mib(snmp)
            
            self.sys_info_d = all_sys_info_d['sys_info']
            self.sys_ip_info_d = all_sys_info_d['sys_ip_info']
            self.sys_snmp_info_d = all_sys_info_d['sys_snmp_info']
            
            self.passmsg = 'Walking system MIB successfully. '
            
            logging.info('System basic info: \n%s, IP info: \n%s, SNMP info: \n%s' \
                         % (self.sys_info_d, self.sys_ip_info_d, self.sys_snmp_info_d))
                
        except Exception, ex:
            self.errmsg = ex.message