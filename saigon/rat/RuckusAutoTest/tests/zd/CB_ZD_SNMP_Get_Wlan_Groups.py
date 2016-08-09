'''
Created on Mar 29, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to get wlans information via ZD SNMP.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import wlan_group_list as wlangroup

class CB_ZD_SNMP_Get_Wlan_Groups(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_wlan_groups()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _get_wlan_groups(self):
        try:
            wlan_group_name_list = []
            if self.conf.has_key('wlan_group_name_list'):
                wlan_group_name_list = self.conf['wlan_group_name_list']
                
            message = wlan_group_name_list if wlan_group_name_list else 'All'
            logging.info('Get WLAN groups information via ZD SNMP: %s' % message)
                     
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))
            snmp = helper.create_snmp(snmp_cfg)
            
            #Dict key is index, need to convert the key as wlan name.
            wlan_groups_dict = wlangroup.get_wlan_groups_by_key_value(snmp)
            
            self.snmp_wlan_groups_dict = wlan_groups_dict
            
            logging.info('SNMP wlan groups info: %s' % self.snmp_wlan_groups_dict)                
        
            self.passmsg = 'Get wlan groups via ZD SNMP successfully: %s' % message
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['snmp_wlan_group_info'] = self.snmp_wlan_groups_dict
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                
        self.errmsg = ''
        self.passmsg = ''