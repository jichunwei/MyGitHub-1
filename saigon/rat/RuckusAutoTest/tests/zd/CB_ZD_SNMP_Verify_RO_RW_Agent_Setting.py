'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify update function with rw setting, get snmp nodes via ro setting.
'''


import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.common.Ratutils import get_random_string
from RuckusAutoTest.common.utils import compare
from RuckusAutoTest.components.lib.zdcli.sys_basic_info import get_sys_info
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import sys_info as sysinfo

class CB_ZD_SNMP_Verify_RO_RW_Agent_Setting(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._verify_rw_agent_setting()
        
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

    def _verify_rw_agent_setting(self):
        logging.info('Verify SNMP agent RO and RW seting')
        
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
                rw_setting = helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw')
                ro_setting = helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro')
            
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr    
            snmp = helper.create_snmp(snmp_cfg)
            
            type = 'alpha'
            new_system_name = get_random_string(type, 1, 32) 
            
            test_cfg = {}
            test_cfg['system_name'] = new_system_name
            logging.info('Set system name with RW setting via ZD SNMP: %s' % (test_cfg,))
            
            snmp.set_config(rw_setting)
            res_update = sysinfo.update_sys_info(snmp, test_cfg)
            
            logging.info('Config: %s, Result: %s' % (test_cfg, res_update))
            
            logging.info('Get system name via ZD CLI')
            basic_info = get_sys_info(self.zdcli)['System Overview']
            if basic_info.has_key('Name'):
                cli_system_name = basic_info['Name']
            else:
                cli_system_name = ''
                
            logging.info('Get system name with RO setting via ZD SNMP')            
            snmp.set_config(ro_setting)
            
            snmp_system_name = sysinfo.get_system_name(snmp)
            
            if compare(snmp_system_name, new_system_name):
                if compare(cli_system_name, snmp_system_name):                    
                    self.passmsg = 'Set value successfully with RW user and the values are same via CLI and SNMP.'                    
                else:
                    self.errmsg = 'The values via CLI and SNMP are not same. CLI: %s, SNMP: %s' % (cli_system_name, snmp_system_name)
                    
            else:
                self.errmsg = 'Error during set value with RW user. Config: %s, Result: %s, SNMP, CLI: %s, SNMP: %s' \
                             % (test_cfg, res_update, cli_system_name, snmp_system_name) 
                
            if self.passmsg:
                logging.info(self.passmsg)
            
            if self.errmsg:
                logging.warning(self.errmsg)
                                    
        except Exception, ex:
            self.errmsg = ex.message