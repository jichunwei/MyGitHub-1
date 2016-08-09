'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify update wlan via SNMP.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import wlan_list as wlan
from RuckusAutoTest.components.lib.snmp.zd import aaa_servers as aaa 


class CB_ZD_SNMP_Verify_Update_Wlan(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._verify_update_wlan_cfg()        
        
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
        self.edit_wlan_cfg_list = self.carrierbag['edit_wlan_cfg_list']
    
    def _update_carrier_bag(self):
        pass

    def _verify_update_wlan_cfg(self):
        logging.info('Verify update wlan config via ZD SNMP')
        try:
            update_wlan_cfg_list = self.edit_wlan_cfg_list
            
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
            snmp = helper.create_snmp(snmp_cfg)
            
            server_id_name_mapping = aaa.get_all_servers_id_name_mapping(snmp)
            wlan_index_name_mapping = wlan.get_wlan_index_value_mapping(snmp)
            if len(wlan_index_name_mapping)>0:
                wlan_id = wlan_index_name_mapping.keys()[0]
                wlan_name = wlan_index_name_mapping.values()[0]
            
            res_d = wlan.verify_update_wlan(snmp, wlan_id, update_wlan_cfg_list, server_id_name_mapping)
            
            if res_d:
                self.errmsg = res_d
            else:
                self.passmsg = 'Update wlan config successfully: %s' % wlan_name
                                    
        except Exception, ex:
            self.errmsg = ex.message
            