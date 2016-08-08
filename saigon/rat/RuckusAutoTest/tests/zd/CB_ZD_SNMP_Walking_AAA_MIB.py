'''
Created on Mar 27, 2011
@author: cherry.cheng@ruckuswireless.com

Description: This script is used to configure system info via zd snmp.
'''


import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.snmp import snmphelper as helper
from RuckusAutoTest.components.lib.snmp.zd import walking_mib as walking

class CB_ZD_SNMP_Walking_AAA_MIB(Test):
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):        
        self._walking_aaa_mib()        
        
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
        self.carrierbag['snmp_server_info_dict'] = self.server_info_d

    def _walking_aaa_mib(self):
        logging.info('Walking AAA server mib and parsing the information')
        try:
            snmp_agent_cfg = self.conf['snmp_agent_cfg']
            snmp_cfg = self.conf['snmp_cfg']
            snmp_cfg['ip_addr'] = self.zdcli.ip_addr
            snmp_cfg.update(helper.get_update_snmp_cfg(snmp_agent_cfg, 'ro'))               
            snmp = helper.create_snmp(snmp_cfg)
            
            self.server_info_d = walking.walking_aaa_mib(snmp)
            
            logging.info('AAA server info: \n%s' % self.server_info_d)
            
            self.passmsg = 'Walking AAA server MIB successfully.'
                
        except Exception, ex:
            self.errmsg = ex.message