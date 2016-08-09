'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
    This script is to get system SNMP information via ZD CLI, include snmp agent v2 and v3, snmp trap.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli.sys_snmp_info import (get_sys_snmpv2_info, 
                                                               get_sys_snmpv3_info, 
                                                               get_sys_snmp_trap_info)
from RuckusAutoTest.components.lib.zdcli.sys_snmp_info import get_sys_snmp_trap_v3_info
class CB_ZD_CLI_Get_Sys_SNMP_Info(Test):
    required_components = ['ZoneDirectorCLI']
    parameter_description = {'info_type': 'Type of snmp setting to get, the values is v2_agent, v3_agent, trap, and all default is all.'}
    
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_sys_snmp_info()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _get_sys_snmp_info(self):
        logging.info('Get system SNMP information via zd cli.')
        
        try:
            if self.conf.has_key('info_type'):
                info_type = self.conf['info_type']
                if info_type == 'all':
                    info_type = ['v2_agent','v3_agent', 'trap']
                elif ',' in info_type:
                    info_type = info_type.split(',')
                else:
                    info_type = [info_type]            
            
            cli_sys_snmp_info = {}
            
            if 'v2_agent' in info_type:
                cli_sys_snmp_info['v2_agent'] = get_sys_snmpv2_info(self.zdcli)
            if 'v3_agent' in info_type:
                cli_sys_snmp_info['v3_agent'] = get_sys_snmpv3_info(self.zdcli)
            if 'trap' in info_type:
                snmp_trap_v3_info = get_sys_snmp_trap_v3_info(self.zdcli)
                if snmp_trap_v3_info.get('Status').lower() == 'enabled':#if v3 is enabled,  return v3 trap info, else return v2 trap info
                    cli_sys_snmp_info['trap'] = snmp_trap_v3_info
                else:
                    snmp_trap_v2_info = get_sys_snmp_trap_info(self.zdcli)
                    cli_sys_snmp_info['trap'] = snmp_trap_v2_info
            
            self.zdcli_sys_snmp_info = cli_sys_snmp_info
            
            self.passmsg = 'Get system SNMP information via ZD CLI successfully: %s' % self.zdcli_sys_snmp_info
            logging.info('System SNMP information: %s' % self.zdcli_sys_snmp_info)
        
        except Exception, ex:
            self.errmsg = ex.message
        
    def _init_test_params(self, conf):
        self.conf = {'info_type': 'v2_agent,v3_agent'}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['zdcli_sys_snmp_info'] = self.zdcli_sys_snmp_info  