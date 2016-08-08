'''
Description:
Created on 2011-03-05
@author: cherry.cheng@ruckuswireless.com
Enable snmp trap version 2 and version 3 by zd cli.
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_trap

class CB_ZD_CLI_Set_SNMP_Trap(Test):
    '''
    '''
    required_components = ['ZoneDirectorCLI']
    parameter_description = {'snmp_trap_cfg': 'SNMP trap config will be set'}
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
    def test(self):
        if self.conf.has_key('snmp_trap_cfg'):
            snmp_trap_cfg = self.conf['snmp_trap_cfg']
            logging.info("Set SNMP trap with config: %s" % snmp_trap_cfg)
            result, res_dict = config_snmp_trap(self.zdcli, snmp_trap_cfg)
            
            if not result:
                self.errmsg = 'Config snmp trap fail. Config: %s, Error: %s' % (snmp_trap_cfg, res_dict)
        else:
            self.errmsg = 'No snmp trap config.'
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()   
            return self.returnResult('PASS', 'Set SNMP Trap via CLI successfully')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        #@author: chentao @2013-08-29  to support ZD_SR testbed
        if self.conf.has_key('target_zd') and self.conf['target_zd']:
            if self.conf['target_zd'] == 'zd1':
                self.zdcli = self.testbed.components['ZDCLI1']
            else:
                self.zdcli = self.testbed.components['ZDCLI2'] 
        else:
            self.zdcli = self.testbed.components['ZoneDirectorCLI']
        #@author: chentao @2013-08-29  to support ZD_SR testbed
               
        self.errmsg = ''
        self.passmsg = ''  