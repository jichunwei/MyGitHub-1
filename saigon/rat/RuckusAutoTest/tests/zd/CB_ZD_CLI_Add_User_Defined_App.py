'''
Created on 2014-06-17
@author: chen.tao@odc-ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import application_visibility as vap

class CB_ZD_CLI_Add_User_Defined_App(Test):

    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        try:
            logging.info('Start to add user defined app via cli!')
            if self.conf['user_app_num']:
                self.create_specified_num_of_user_apps(self.conf['user_app_num'])
            else:
                vap.add_user_defined_application_rule(self.zdcli,self.conf['user_app_cfg'],self.conf['overwrite'])
        except: 
            self.errmsg = 'Adding user defined app(s) failed.' 
        self.passmsg = 'Adding user defined app(s) succeeded.'
        if self.conf['negative']:
            if self.errmsg:
                return self.returnResult('PASS', self.errmsg)
            return self.returnResult('FAIL', self.passmsg)
        else:
            if self.errmsg:
                return self.returnResult('FAIL', self.errmsg)
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass

    def create_specified_num_of_user_apps(self,num):
        if num <=1 : raise Exception('Please provide a num bigger than 1')
        for i in range(1,num+1):
            dict1 = {}
            ip_addr = '1.1.1.%s'%i
            port = str(20000+i)
            description='user_app_test_%s'%i
            dict1= dict(rule_description = description,dest_ip=ip_addr,dest_port=port,netmask='255.255.255.0',protocol='tcp')
            vap.add_user_defined_application_rule(self.zdcli,[dict1],True)
            del dict1

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'user_app_cfg':[],
                     'negative': False,
                     'overwrite':False,
                     'user_app_num':0,}#max num is 32
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
