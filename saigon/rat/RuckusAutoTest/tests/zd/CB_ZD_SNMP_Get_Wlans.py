'''
Created on Mar 29, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to get wlans information via ZD SNMP.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import wlan_list as wlan
from RuckusAutoTest.components.lib.snmp.zd import aaa_servers as aaa

class CB_ZD_SNMP_Get_Wlans(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_wlans()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _get_wlans(self):
        try:
            wlan_name_list = []
            if self.conf.has_key('wlan_name_list'):
                wlan_name_list = self.conf['wlan_name_list']
                
            message = wlan_name_list if wlan_name_list else 'ALL'
            
            logging.info('Get Wlans information via ZD SNMP: %s' % message)
                     
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))
            snmp = helper.create_snmp(snmp_cfg)
            
            server_id_name_mapping = aaa.get_all_servers_id_name_mapping(snmp)
            #Dict key is index, need to convert the key as wlan name.
            wlans_dict = wlan.get_wlans_by_key_value(snmp, server_id_name_mapping)
            
            self.snmp_wlans_dict = wlans_dict
            
            logging.info('SNMP wlans info: %s' % self.snmp_wlans_dict)

            self.passmsg = 'Get wlans via ZD SNMP successfully: %s' % message
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['snmp_wlan_info'] = self.snmp_wlans_dict
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                
        self.errmsg = ''
        self.passmsg = ''