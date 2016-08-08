'''
Description:
   Set snmp trap format via CLI
   
Created on 2012-06-28
@author: zoe.huang@ruckuswireless.com

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_trap_format

class CB_ZD_CLI_Set_SNMP_Trap_Format(Test):
    
    required_components = ['ZoneDirectorCLI']
    parameter_description = {'version': 'snmp trap format, value is 2 or 3'}
    
    def config(self, conf):
        self._init_test_params(conf)
        
    def test(self):
        if self.conf.has_key('version'):
            version = self.conf['version']
            logging.info('Set SNMP trap format to SNMPv%s' %  version)
            result, res_dict = config_snmp_trap_format(self.zdcli, version)           
            if not result:
                self.errmsg = 'Set snmp trap format to SNMPv%s failed, Error reason: %s' % (version, res_dict)
        else:
            self.errmsg = 'No snmp trap format config.'
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:  
            return self.returnResult('PASS', 'Set SNMP Trap format via CLI successfully')
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        self.errmsg = ''
        self.passmsg = ''  