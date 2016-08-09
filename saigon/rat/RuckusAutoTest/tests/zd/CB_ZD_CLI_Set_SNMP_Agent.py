'''
Description:
Created on 2011-03-05
@author: cherry.cheng@ruckuswireless.com
Enable snmp agent version 2 and version 3 by zd cli.
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli.configure_snmp import config_snmp_agent

class CB_ZD_CLI_Set_SNMP_Agent(Test):
    '''
    '''
    required_components = ['ZoneDirectorCLI']
    parameter_description = {'snmp_agent_cfg': 'SNMP agent config will be set'}
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
    def test(self):
        if self.conf.has_key('snmp_agent_cfg'):
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            logging.info("Set SNMP agent with config: %s" % snmp_agent_cfg)
            result, res_dict = config_snmp_agent(self.zdcli, snmp_agent_cfg)
            
            if not result:
                self.errmsg = 'Config snmp agent fail. Config: %s, Error: %s' % (snmp_agent_cfg, res_dict)
        else:
            self.errmsg = 'No snmp agent config.'
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:   
            self._update_carrier_bag()
            return self.returnResult('PASS', 'Set SNMP Agent via CLI successfully')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        self.errmsg = ''
        self.passmsg = ''  