'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify continue walking to get system basic information.
'''

import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import snmp_agent_trap as snmpagent


class CB_ZD_SNMP_Verify_SNMP_Commands(Test):
    def config(self, conf):        
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_snmp_commands()        
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

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

    def _verify_snmp_commands(self):
        logging.info('Verify snmp commands')
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr            
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))
            snmp = helper.create_snmp(snmp_cfg)
            
            is_enable = snmp_agent_cfg['enabled']
            
            res = snmpagent.verify_snmp_command(snmp, self.zdcli, is_enable)
            
            if res:
                self.errmsg = res
            else:
                if is_enable:
                    self.passmsg = 'SNMP commands works well when agent is enabled.'
                else:
                    self.passmsg = "SNMP commands can't get information when agent is disabled."
            
        except Exception, ex:
            self.errmsg = ex.message         