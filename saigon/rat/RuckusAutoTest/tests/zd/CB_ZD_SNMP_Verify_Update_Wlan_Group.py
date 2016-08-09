'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify update wlan via SNMP.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import wlan_group_list as wlangroup

class CB_ZD_SNMP_Verify_Update_Wlan_Group(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._verify_update_wlan_group_cfg()        
        
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
        if self.carrierbag.has_key('edit_wlan_group_cfg_list'):
            self.edit_wlan_group_cfg_list = self.carrierbag['edit_wlan_group_cfg_list']
    
    def _update_carrier_bag(self):
        pass

    def _verify_update_wlan_group_cfg(self):
        logging.info('Verify update wlan group config via ZD SNMP')
        try:
            if self.conf.has_key('edit_wlan_group_cfg_list'):
                edit_wlan_group_cfg_list = self.conf['edit_wlan_group_cfg_list']
            else:
                edit_wlan_group_cfg_list = self.edit_wlan_group_cfg_list
            
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
            snmp = helper.create_snmp(snmp_cfg)
            
            group_id_name_mapping = wlangroup.get_wlan_group_index_value_mapping(snmp)
            if group_id_name_mapping.has_key('1'):
                group_id_name_mapping.pop('1')
                
            if group_id_name_mapping and len(group_id_name_mapping) > 1:                
                group_id = group_id_name_mapping.keys()[0]
                group_name = group_id_name_mapping[group_id]            
            
            res_d = wlangroup.verify_update_wlan_group(snmp, group_id, edit_wlan_group_cfg_list)
            
            if res_d:
                self.errmsg = res_d
            else:
                self.passmsg = 'Update wlan group config successfully: %s' % group_name
                                    
        except Exception, ex:
            self.errmsg = ex.message
            