'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify aaa servers information between SNMP get and SNMP set.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp.zd import aaa_servers as aaa


class CB_ZD_SNMP_Verify_AAA_Servers_SNMP_Get_Set(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_servers_get_set()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.server_cfg_dict = self.carrierbag['snmp_server_info_dict']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''

    def _verify_servers_get_set(self):
        logging.info('Verify AAA servers information between SNMP set and get')
        try:
            server_cfg_list = self.conf['server_cfg_list']
            snmp_set_cfg_dict = {}
            for server_cfg in server_cfg_list:
                server_name = server_cfg['server_name']
                snmp_set_cfg_dict[server_name] = server_cfg
                
            snmp_get_cfg_dict = self.server_cfg_dict
            
            res_d = aaa.verify_servers_test_data_snmp(snmp_get_cfg_dict, snmp_set_cfg_dict)
            
            self.errmsg = res_d
            self.passmsg = 'AAA servers information are same between SNMP get and SNMP set.'    
            
        except Exception, ex:
            self.errmsg = ex.message    