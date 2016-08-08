'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to verify update server config via SNMP.

'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import aaa_servers as aaa


class CB_ZD_SNMP_Verify_Update_AAA_Server(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._verify_update_aaa_server_cfg()        
        
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

    def _verify_update_aaa_server_cfg(self):
        logging.info('Verify update AAA server via ZD SNMP')
        try:
            server_name = self.conf['server_name']            
            update_server_cfg_list = self.conf['update_server_cfg_list']
            
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
            snmp = helper.create_snmp(snmp_cfg)
            
            server_id = aaa.get_server_id_by_name(snmp, server_name)
            if not server_id:
                raise Exception("AAA server[%s] is not created" % server_name)
            res_d = aaa.verify_update_server(snmp, server_id, update_server_cfg_list)
            
            if res_d:
                self.errmsg = res_d
            else:
                self.passmsg = 'Update server config successfully: %s' % server_name
                                    
        except Exception, ex:
            self.errmsg = ex.message          