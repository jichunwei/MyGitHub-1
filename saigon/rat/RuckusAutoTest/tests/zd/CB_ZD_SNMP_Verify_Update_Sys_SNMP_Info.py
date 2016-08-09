'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify update wlan via SNMP.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import sys_snmp_info as snmpinfo

class CB_ZD_SNMP_Verify_Update_Sys_SNMP_Info(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._verify_update_sys_snmp_info()
        
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

    def _verify_update_sys_snmp_info(self):
        logging.info('Verify update system SNMP info via ZD SNMP')
        try:
            if self.conf.has_key('snmp_agent_cfg'):
                snmp_agent_cfg = self.conf['snmp_agent_cfg']
            else:
                snmp_agent_cfg = {}
                
            if self.conf.has_key('snmp_cfg'):
                snmp_cfg = self.conf['snmp_cfg']
            else:
                snmp_cfg = {'version': 2,
                            'timeout': 30,
                            'retries': 5, 
                            'enabled': True,
                            'ro_community': 'rotest',
                            'rw_community': 'rwtest',
                            }
            if snmp_agent_cfg:
                snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
                
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp = helper.create_snmp(snmp_cfg)
            
            if self.conf.has_key('set_snmp_cfg'):
                test_data_cfg = self.conf['set_snmp_cfg']
            else:
                test_data_cfg = snmpinfo.gen_test_data_sys_snmp_info()
            
            snmpinfo.set_sys_snmp_info(snmp, test_data_cfg)
            snmp_sys_snmp_info = snmpinfo.get_sys_snmp_info(snmp)
            
            new_test_data_cfg = self._convert_test_data_cfg(test_data_cfg)
            
            res_d = snmpinfo.verify_sys_snmp_info_snmp_test_data(snmp_sys_snmp_info, new_test_data_cfg)
            
            if res_d:
                self.errmsg = res_d
            else:
                self.passmsg = 'Update system SNMP info successfully.'
                                    
        except Exception, ex:
            self.errmsg = ex.message
            
            
    def _convert_test_data_cfg(self, test_data_cfg):
        new_test_data_cfg = {}
        new_test_data_cfg.update(test_data_cfg)
        
        trap_v3_obj_list = ['v3_trap_user','v3_trap_server', 'v3_trap_auth','v3_trap_auth_key','v3_trap_priv','v3_trap_priv_key']
        
        trap_server_info = {}
        
        if new_test_data_cfg.has_key('v2_trap_server'):
            trap_server_info['v2_trap_server'] = new_test_data_cfg.pop('v2_trap_server')
        
        for name in trap_v3_obj_list:
            if new_test_data_cfg.has_key(name):
                trap_server_info[name] = new_test_data_cfg.pop(name)
            
        if trap_server_info:
            new_test_data_cfg.update({'1': trap_server_info})
            
        return new_test_data_cfg