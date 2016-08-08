'''
Created on 2014-06-17
@author: chen.tao@odc-ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import application_visibility as vap
class CB_ZD_CLI_Application_Visibility_Init_Env(Test):

    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        try:
            logging.info('Start to clear all application visibility configs!')
            vap.delete_all_user_defined_apps(self.zdcli)
            vap.delete_all_app_port_mapping(self.zdcli)
            vap.delete_all_app_denial_policy(self.zdcli)
        except: 
            self.errmsg = 'Init env failed.'                                  
            return self.returnResult('FAIL', self.errmsg)
        self.passmsg = 'Init env succeeded.'
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