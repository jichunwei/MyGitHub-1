'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify delete wlans via SNMP.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import aps_info


class CB_ZD_SNMP_Verify_Delete_APs(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._delete_aps()        
                
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

    def _delete_aps(self):
        logging.info('Verify delete aps via ZD SNMP')
        try:
            if self.conf.has_key('is_wait_ap_join'):
                is_wait_ap_join = self.conf['is_wait_ap_join']
            else:
                is_wait_ap_join = True
                
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))               
            snmp = helper.create_snmp(snmp_cfg)
            
            zd_ap_id_mac_mapping = aps_info.get_zd_ap_index_value_mapping(snmp)     
            if self.conf.has_key('delete_ap_mac_list'): 
                ap_mac_addr_list = self.conf['delete_ap_mac_list']
            else:
                ap_mac_addr_list = zd_ap_id_mac_mapping.values()
                
            if ap_mac_addr_list:
                err_mac_addr_list = aps_info.verify_delete_aps(snmp, ap_mac_addr_list, is_wait_ap_join)
                if err_mac_addr_list:                
                    self.errmsg = 'The following aps are not deleted: %s' % err_mac_addr_list
            else:
                self.errmsg = 'No AP to delete.'
                
            self.passmsg = 'The aps are deleted: %s' % ap_mac_addr_list 
                                    
        except Exception, ex:
            self.errmsg = ex.message
            