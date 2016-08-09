'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description:  This script is used to verify wlans information between SNMP set and SNMP get.
'''

import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import wlan_list as wlan
from RuckusAutoTest.components.lib.snmp.zd import aaa_servers as aaa


class CB_ZD_SNMP_Verify_Wlans_SNMP_Get_Set(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_wlans_get_set()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.create_wlans_dict = self.carrierbag['create_wlan_cfg_dict']
        self.snmp_wlans_dict = self.carrierbag['snmp_wlan_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                
        self.errmsg = ''
        self.passmsg = ''

    def _verify_wlans_get_set(self):
        logging.info('Verify wlans information SNMP get and SNMP set')
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
            snmp = helper.create_snmp(snmp_cfg)
            
            server_id_name_mapping = aaa.get_all_servers_id_name_mapping(snmp)
            
            snmp_set_cfg_dict = {}
            for index, wlan_cfg in self.create_wlans_dict.items():
                snmp_set_cfg_dict[index] = wlan.convert_wlan_test_data_cfg(wlan_cfg, server_id_name_mapping)
        
            snmp_get_cfg_dict = self.snmp_wlans_dict
            
            self.errmsg = wlan.verify_wlans_test_data_snmp(snmp_get_cfg_dict, snmp_set_cfg_dict)
            self.passmsg = 'Wlan info are same between SNMP get and SNMP set.'
            
        except Exception, ex:
            self.errmsg = ex.message    