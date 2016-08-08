'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify delete wlans via SNMP.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper 
from RuckusAutoTest.components.lib.snmp.zd import wlan_list as wlan


class CB_ZD_SNMP_Verify_Delete_Wlans(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._delete_wlans()        
        
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

    def _delete_wlans(self):
        logging.info('Verify delete wlans via ZD SNMP')
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))               
            snmp = helper.create_snmp(snmp_cfg)
            
            wlan_index_name_mapping = wlan.get_wlan_index_value_mapping(snmp)
                
            if wlan_index_name_mapping:
                err_index_list = wlan.delete_wlans(snmp, wlan_index_name_mapping.keys())
                
                if err_index_list:
                    err_wlan_name_list = []
                    for wlan_id in err_index_list:
                        err_wlan_name_list.append(wlan_index_name_mapping[str(wlan_id)])
                    self.errmsg = 'The following wlans are not deleted: %s' % err_wlan_name_list
            else:
                self.errmsg = 'No wlan to delete.'
            
            self.passmsg = 'The wlans are deleted: %s' % wlan_index_name_mapping.values() 
                                    
        except Exception, ex:
            self.errmsg = ex.message
            