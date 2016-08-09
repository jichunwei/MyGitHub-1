'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify aaa servers information between SNMP get and CLI get.
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp.zd import aaa_servers as aaa

class CB_ZD_SNMP_Verify_AAA_Servers_SNMPGet_CLIGet(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._verify_servers_snmp_cli_get()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.zdcli_server_info_list = self.carrierbag['zdcli_server_info_list']
        self.snmp_server_info_dict = self.carrierbag['snmp_server_info_dict']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):        
        self.errmsg = ''
        self.passmsg = ''

    def _verify_servers_snmp_cli_get(self):
        logging.info('Verify AAA servers information between SNMP get and CLI get')
        try:
            zdcli_server_info_dict = {}
            for server_cfg in self.zdcli_server_info_list:
                if server_cfg.has_key('Name'):
                    server_name = server_cfg['Name']
                    zdcli_server_info_dict[server_name] = server_cfg
                
            snmp_server_info_dict = self.snmp_server_info_dict
            
            res_d = aaa.verify_servers_dict_snmp_cli(snmp_server_info_dict, zdcli_server_info_dict)
            
            self.errmsg = res_d
            self.passmsg = 'AAA servers info are same between SNMP get and CLI get.'
            
        except Exception, ex:
            self.errmsg = ex.message      
    