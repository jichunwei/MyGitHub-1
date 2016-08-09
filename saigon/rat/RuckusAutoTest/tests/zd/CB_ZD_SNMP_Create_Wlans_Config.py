'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is to create wlans based on config. 
'''
import logging
from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import wlan_list as wlan
from RuckusAutoTest.components.lib.snmp.zd import aaa_servers as aaa

class CB_ZD_SNMP_Create_Wlans_Config(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self._create_wlan_config()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()             
            return self.returnResult('PASS', self.passmsg)    
    
    def cleanup(self):
        pass
    
    def _create_wlan_config(self):
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))
            snmp = helper.create_snmp(snmp_cfg)
        
            aaa_auth_server_id = aaa.get_auth_server_id(snmp)
            aaa_acct_server_id = aaa.get_acct_server_id(snmp)
            self.create_wlan_cfg_list = wlan.gen_wlan_test_cfg(aaa_auth_server_id, aaa_acct_server_id)
            self.edit_wlan_cfg_list = wlan.gen_wlan_update_cfg(aaa_auth_server_id, aaa_acct_server_id)
            
            logging.info('Wlan config: %s' % self.edit_wlan_cfg_list)
            self.passmsg = 'Wlans config are created successfully.'            
                                    
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
        self.carrierbag['create_wlan_cfg_list'] = self.create_wlan_cfg_list
        self.carrierbag['edit_wlan_cfg_list'] = self.edit_wlan_cfg_list   