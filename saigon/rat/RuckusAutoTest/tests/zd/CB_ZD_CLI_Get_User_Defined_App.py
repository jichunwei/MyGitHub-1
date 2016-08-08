'''
Created on 2014-06-17
@author: chen.tao@odc-ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import application_visibility as vap

class CB_ZD_CLI_Get_User_Defined_App(Test):

    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        try:
            logging.info('Start to get user defined app via cli!')
            if self.conf['user_app_description']:
                one_user_app = vap.get_user_deined_app_rule_info_by_description(self.zdcli,self.conf['user_app_description'])
                user_defined_apps = {self.conf['user_app_description']:one_user_app}
                self._update_carrier_bag(user_defined_apps)
            else:
                user_defined_apps = vap.get_all_user_defined_apps(self.zdcli)
                self._update_carrier_bag(user_defined_apps)
        except: 
            self.errmsg = 'Getting user defined app(s) failed.'                                  
            return self.returnResult('FAIL', self.errmsg)
        self.passmsg = 'Getting user defined app(s) succeeded.'
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'user_app_description':''}
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
    def _update_carrier_bag(self,user_defined_apps):
        self.carrierbag['user_defined_apps'] = user_defined_apps
