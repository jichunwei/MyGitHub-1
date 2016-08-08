'''
Author: Cherry Cheng
Email: cherry.cheng@ruckuswireless.com
Description: 
    This script is to get system SNMP trap information via ZD CLI.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli.sys_snmp_info import get_sys_snmp_trap_info
from RuckusAutoTest.components.lib.zdcli.sys_snmp_info import get_sys_snmp_trap_v3_info
class CB_ZD_CLI_Get_Sys_SNMP_Trap_Info(Test):
    required_components = ['ZoneDirectorCLI']
    parameter_description = {}
    
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_sys_snmp_trap_info()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _get_sys_snmp_trap_info(self):
        logging.info('Get system SNMP Trap information via zd cli.')
        
        try:
            snmp_trap_v3_info = get_sys_snmp_trap_v3_info(self.zdcli)
            
            if snmp_trap_v3_info.get('Status').lower() == 'enabled':#if v3 is enabled,  return v3 trap info.
                self.zdcli_sys_snmp_trap_info = snmp_trap_v3_info
            else:#no matter v2 is enabled or not, return v2 trap info.
                snmp_trap_v2_info = get_sys_snmp_trap_info(self.zdcli)
                self.zdcli_sys_snmp_trap_info = snmp_trap_v2_info
            
            self.passmsg = 'Get system SNMP Trap information via ZD CLI successfully: %s' % self.zdcli_sys_snmp_trap_info
            logging.info('System SNMP trap information: %s' % self.zdcli_sys_snmp_trap_info)
        
        except Exception, ex:
            self.errmsg = ex.message
        
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['zdcli_sys_snmp_trap_info'] = self.zdcli_sys_snmp_trap_info  