'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify delete wlan groups via SNMP.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import wlan_group_list as wlangroup


class CB_ZD_SNMP_Verify_Delete_Wlan_Groups(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._verify_delete_wlan_groups()        
        
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
        pass
    
    def _update_carrier_bag(self):
        pass

    def _verify_delete_wlan_groups(self):
        logging.info('Verify delete wlan groups via ZD SNMP')
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))               
            snmp = helper.create_snmp(snmp_cfg)
            
            group_id_name_mapping = wlangroup.get_wlan_group_index_value_mapping(snmp)
            
            #Default group (id=1) can not be deleted.
            if group_id_name_mapping.has_key('1'):
                group_id_name_mapping.pop('1')
             
            if group_id_name_mapping:
                err_index_list = wlangroup.delete_wlan_groups(snmp, group_id_name_mapping.keys())
                if err_index_list:
                    err_wlan_group_name_list = []
                    for wlan_group_id in err_index_list:
                        err_wlan_group_name_list.append(group_id_name_mapping[str(wlan_group_id)])
                    
                    group_id_name_mapping = wlangroup.get_wlan_group_index_value_mapping(snmp)
                    self.errmsg = 'The following wlan groups are not deleted: %s; Current Wlan Groups: %s; Error Group ID List:%s' \
                                      % (err_wlan_group_name_list, group_id_name_mapping, err_index_list)
            else:
                self.errmsg = 'No wlan group to delete.'
                    
            self.passmsg = 'The wlan groups are deleted: %s' % group_id_name_mapping.values() 
                                    
        except Exception, ex:
            self.errmsg = ex.message
            