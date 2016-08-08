'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to configure aaa servers in ZD CLI.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import aaa_servers


class CB_ZD_SNMP_Config_AAA_Servers(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._config_aaa_servers()        
        
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

    def _config_aaa_servers(self):
        logging.info('Create AAA servers via ZD SNMP')
        try:
            server_cfg_list = self.conf['server_cfg_list']
            server_name_list = self.conf['server_name_list']
            
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
            snmp = helper.create_snmp(snmp_cfg)
            
            logging.info('Server config: %s' % server_cfg_list)
            err_server_name_list = aaa_servers.create_aaa_servers(snmp, server_cfg_list)
            
            if err_server_name_list:
                self.errmsg = "The servers are not created successfully: %s" % err_server_name_list
            else:
                self.passmsg = 'The servers are created successfully:' % server_name_list 
                                    
        except Exception, ex:
            self.errmsg = ex.message