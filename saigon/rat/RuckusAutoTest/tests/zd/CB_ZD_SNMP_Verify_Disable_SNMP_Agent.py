'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify aaa servers information between SNMP get and SNMP set.
'''

import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import sys_snmp_info
from RuckusAutoTest.components.lib.zdcli import sys_snmp_info as lib

class CB_ZD_SNMP_Verify_Disable_SNMP_Agent(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_disable_snmp_agent()
        
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

    def _verify_disable_snmp_agent(self):
        logging.info('Verify Disable SNMP Agent via SNMP')
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))               
            snmp = helper.create_snmp(snmp_cfg)
            
            version = str(snmp_agent_cfg['version'])
            
            test_data_cfg = {}
            key = 'v%s_enable' % version
            test_data_cfg[key] = '2'  #Disabled        
        
            # Disbale snmp agent v2 and v3.
            sys_snmp_info.set_sys_snmp_info(snmp, test_data_cfg, is_update_snmp_cfg = False)
            
            import time
            time.sleep(20)
            
            enabled = ''
            if version == '2':
                snmp_agent = lib.get_sys_snmpv2_info(self.zdcli)                
                if snmp_agent.has_key('Status'):
                    enabled = snmp_agent['Status']
            else:
                snmp_agent = lib.get_sys_snmpv3_info(self.zdcli)
                if snmp_agent.has_key('status'):
                    enabled = snmp_agent['status']
                
            if enabled:
                if helper.is_disabled(enabled):
                    self.passmsg = 'Disable snmp agent v%s via SNMP successfully.' % version
                else:
                    self.errmsg = "Disable snmp agent v%s failed. Actual: %s" % (version, enabled)
            else:
                self.errmsg = "Didn't get snmp agent v%s enabled setting via ZD CLI. CLI values: %s" % (version, snmp_agent)
            
        except Exception, ex:
            self.errmsg = ex.message