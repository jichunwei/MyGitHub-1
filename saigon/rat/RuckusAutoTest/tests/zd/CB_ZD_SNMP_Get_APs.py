'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to get aps information via ZD SNMP.

'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import aps_info


class CB_ZD_SNMP_Get_APs(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_aps()
                
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else: 
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _get_aps(self):
        try:
            if self.conf.has_key('ap_mac_list'):
                ap_mac_list = self.conf['ap_mac_list']
            else:
                ap_mac_list = []
            
            message = ''            
            if not ap_mac_list:
                message = 'ALL'
            else:
                message = ap_mac_list
                
            logging.info('Get APs via ZD SNMP: %s' % message)
                     
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))
                           
            snmp = helper.create_snmp(snmp_cfg)
            self.ap_info_dict = aps_info.get_zd_aps_by_mac_addr(snmp, ap_mac_list)
            
            logging.info('SNMP ZD AP list: %s' % self.ap_info_dict)
            self.passmsg = 'Get AP information via ZD SNMP successfully: %s' % message
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['snmp_ap_info_dict'] = self.ap_info_dict
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                
        self.errmsg = ''
        self.passmsg = ''