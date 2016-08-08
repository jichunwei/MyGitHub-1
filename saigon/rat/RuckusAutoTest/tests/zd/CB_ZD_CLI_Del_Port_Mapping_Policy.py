'''
Created on 2014-06-17
@author: chen.tao@odc-ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import application_visibility as vap

class CB_ZD_CLI_Del_Port_Mapping_Policy(Test):

    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        try:
            logging.info('Start to delete app port mapping via cli!')
            vap.delete_all_app_port_mapping(self.zdcli)
        except: 
            self.errmsg = 'Deleting port mapping policy failed.'                                  
            return self.returnResult('FAIL', self.errmsg)
        self.passmsg = 'Deleting port mapping policy succeeded.'
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {}
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
