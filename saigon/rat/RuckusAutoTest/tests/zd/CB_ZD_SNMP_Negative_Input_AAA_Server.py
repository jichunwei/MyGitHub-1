'''
Created on Mar 28, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to configure aaa servers in ZD CLI.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import aaa_servers


class CB_ZD_SNMP_Negative_Input_AAA_Server(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._verify_negative_input_aaa()        
        
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

    def _verify_negative_input_aaa(self):
        logging.info('Verify negative input for aaa servers.')
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'rw'))
            snmp = helper.create_snmp(snmp_cfg)
            
            server_id_name_mapping = aaa_servers.get_server_index_value_mapping(snmp)        
            index = helper.get_dict_key_by_value(server_id_name_mapping, self.conf['server_name'])
            
            if not index:
                res_aaa_d = {'Error': 'No aaa server for name %s' % self.conf['server_name']}
            else:
                res_aaa_d = aaa_servers.update_server_cfg_one_by_one(snmp, index, aaa_servers.gen_server_test_cfg_negative())
            
            pass_d, fail_d = helper.verify_error_for_negative(res_aaa_d)
            
            if pass_d:
                logging.info('Pass information: %s' % pass_d)
            if fail_d:
                logging.warning('Error:' % fail_d)
                self.errmsg = fail_d
            else:                
                self.passmsg = 'Error message is correct for negative input.'
                                    
        except Exception, ex:
            self.errmsg = ex.message