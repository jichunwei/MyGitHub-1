'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description:  This script is used to verify wlans information between SNMP set and SNMP get.
'''

import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.snmp.zd import wlan_group_list as wlangroup


class CB_ZD_SNMP_Verify_Wlan_Groups_SNMP_Get_Set(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_wlan_groups_get_set()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.create_wlan_groups_dict = self.carrierbag['snmp_set_wg_cfg_dict']
        self.snmp_wlan_groups_dict = self.carrierbag['snmp_wlan_group_info']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
                
        self.errmsg = ''
        self.passmsg = ''

    def _verify_wlan_groups_get_set(self):
        logging.info('Verify wlan groups information SNMP get and set')
        try:
            snmp_get_cfg_dict = self.snmp_wlan_groups_dict    
            snmp_set_cfg_dict = self.create_wlan_groups_dict
            
            self.errmsg = wlangroup.verify_wlan_groups_test_data_snmp(snmp_get_cfg_dict, snmp_set_cfg_dict)
            self.passmsg = 'Wlan group info are same between SNMP get and SNMP set.'
            
        except Exception, ex:
            self.errmsg = ex.message    