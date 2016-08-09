'''
Created on Mar 27, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to get system SNMP information via ZD SNMP.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import sys_snmp_info as sys_snmp

class CB_ZD_SNMP_Get_Sys_SNMP_Info(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_system_snmp_info()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _get_system_snmp_info(self):
        try:
            logging.info('Get system SNMP information via ZD SNMP.')
                     
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))
                           
            snmp = helper.create_snmp(snmp_cfg)
            
            if self.conf.has_key('info_type'):
                info_type = self.conf['info_type']
                if info_type == 'all':
                    info_type = ['v2_agent','v3_agent', 'trap']
                elif ',' in info_type:
                    info_type = info_type.split(',')
                else:
                    info_type = [info_type]
                
            gui_snmp_info = {}
            
            if 'v2_agent' in info_type:
                sys_snmp_v2_agent_info_d = sys_snmp.get_sys_snmp_agent_v2_info(snmp)
                gui_snmp_info.update(sys_snmp_v2_agent_info_d)
            if 'v3_agent' in info_type:
                sys_snmp_v3_agent_info_d = sys_snmp.get_sys_snmp_agent_v3_info(snmp)
                gui_snmp_info.update(sys_snmp_v3_agent_info_d)
            if 'trap' in info_type:
                sys_snmp_trap_info_d = sys_snmp.get_sys_snmp_trap_info(snmp)
                gui_snmp_info.update(sys_snmp_trap_info_d)
                
            self.snmp_sys_snmp_info = gui_snmp_info
            
            logging.info('SNMP system SNMP information: %s' % self.snmp_sys_snmp_info)
            self.passmsg = 'Get system SNMP information via ZD SNMP successfully: %s' % self.snmp_sys_snmp_info  
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['snmp_sys_snmp_info'] = self.snmp_sys_snmp_info
    
    def _init_test_params(self, conf):
        self.conf = {'info_type': 'v2_agent,v3_agent'}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                
        self.errmsg = ''
        self.passmsg = ''