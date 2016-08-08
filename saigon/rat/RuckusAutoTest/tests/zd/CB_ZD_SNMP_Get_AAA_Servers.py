'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to get aaa servers information via ZD SNMP.

'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import aaa_servers as aaa


class CB_ZD_SNMP_Get_AAA_Servers(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._get_aaa_servers()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _get_aaa_servers(self):
        try:
            if self.conf.has_key('server_name_list'):
                server_name_list = self.conf['server_name_list']
            else:
                server_name_list = []
            
            message = ''            
            if server_name_list:
                message = 'ALL'
            else:
                message = server_name_list
                
            logging.info('Get AAA servers via ZD SNMP: %s' % message)
                     
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))
                           
            snmp = helper.create_snmp(snmp_cfg)
            self.server_cfg_dict = aaa.get_server_by_name(snmp, server_name_list)
            
            logging.info('SNMP AAA server list: %s' % self.server_cfg_dict)
            self.passmsg = 'Get AAA servers information via ZD SNMP successfully: %s' % message
            
        except Exception, ex:
            self.errmsg = ex.message
            
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['snmp_server_info_dict'] = self.server_cfg_dict
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
                
        self.errmsg = ''
        self.passmsg = ''