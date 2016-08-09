'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify delete servers via SNMP.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd  import aaa_servers as aaa


class CB_ZD_SNMP_Verify_Delete_AAA_Servers(Test):
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
        logging.info('Configure aaa servers in ZD CLI')
        try:
            server_name_list = self.conf['server_name_list']
            
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))               
            snmp = helper.create_snmp(snmp_cfg)
            
            if server_name_list:
                err_server_name_list = aaa.verify_delete_servers(snmp,server_name_list)
                if err_server_name_list:
                    self.errmsg = 'The following servers are not deleted(%s).' % err_server_name_list
            else:
                self.errmsg = 'No AAA server to delete.'
                
            self.passmsg = 'The servers are deleted: %s' % server_name_list
                                            
        except Exception, ex:
            self.errmsg = ex.message
            