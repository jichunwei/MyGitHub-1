'''
Created on Mar 29, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is verify wlan, wlan group, aaa server can only get by snmp v3.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import wlan_list as wlan
from RuckusAutoTest.components.lib.snmp.zd import aaa_servers as aaa
from RuckusAutoTest.components.lib.snmp.zd import wlan_group_list as wlangroup

class CB_ZD_SNMP_Verify_Only_V3_Nodes(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_only_v3_nodes()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _verify_only_v3_nodes(self):
        logging.info('Verify only v3 nodes: Wlan, Wlan group, AAA servers')
        try:
            
            snmp_agent_v3_cfg = self.conf['snmp_agent_v3_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_v3_cfg, 'ro'))                           
            snmpv3 = helper.create_snmp(snmp_cfg)
            
            snmp_agent_v2_cfg = self.conf['snmp_agent_v2_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_v2_cfg, 'ro'))                           
            snmpv2 = helper.create_snmp(snmp_cfg)
            
            #Get wlan, wlan group, aaa server by snmp v3.
            v3_wlan_index_name_mapping = wlan.get_wlan_index_value_mapping(snmpv3) 
            v3_wlan_group_index_name_mapping = wlangroup.get_wlan_group_index_value_mapping(snmpv3)
            v3_aaa_index_name_mapping = aaa.get_server_index_value_mapping(snmpv3)
            
            error_list = []
            if len(v3_wlan_group_index_name_mapping) == 0:
                error_list.append('No wlan group.')
            if len(v3_wlan_index_name_mapping) == 0:
                error_list.append('No wlan.')
            if len(v3_aaa_index_name_mapping) == 0:
                error_list.append('No aaa server.')
            
            if not error_list:
                #Get wlan, wlan group, aaa server by snmp v2.
                v2_wlan_index_name_mapping = wlan.get_wlan_index_value_mapping(snmpv2) 
                v2_wlan_group_index_name_mapping = wlangroup.get_wlan_group_index_value_mapping(snmpv2)
                v2_aaa_index_name_mapping = aaa.get_server_index_value_mapping(snmpv2)
                
                if len(v2_wlan_index_name_mapping) > 0:
                    error_list.append('Can get wlan information via SNMP v2: %s' % v2_wlan_index_name_mapping)
                if len(v2_wlan_group_index_name_mapping) > 0:
                    error_list.append('Can get wlan group information via SNMP v2: %s' % v2_wlan_group_index_name_mapping)
                if len(v2_aaa_index_name_mapping) > 0:
                    error_list.append('Can get AAA server information via SNMP v2: %s' % v2_aaa_index_name_mapping)
            
            self.errmsg = error_list
            self.passmsg = 'Wlan, wlan group, aaa server can not get via SNMP v2.'
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
                
        self.errmsg = ''
        self.passmsg = ''