'''
Created on 2014-06-17
@author: chen.tao@odc-ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import application_visibility as vap

class CB_ZD_CLI_Add_Port_Mapping_Policy(Test):

    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        try:
            logging.info('Start to add port mapping policy via cli!')
            if self.conf['port_mapping_num']:
                self.create_specified_num_of_port_mapping_policy(self.conf['port_mapping_num'])
            else:    
                vap.add_app_port_mapping_rule(self.zdcli,self.conf['port_mapping_cfg'],self.conf['overwrite'])
        except: 
            self.errmsg = 'Adding port mapping policy failed.'
        self.passmsg = 'Adding port mapping policy succeeded.'                                  
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

    def create_specified_num_of_port_mapping_policy(self,num):
        if num <=1 : raise Exception('Please provide a num bigger than 1')
        for i in range(1,num+1):
            dict1 = {}
            port = str(20000+i)
            description='port_mapping_test_%s'%i
            dict1= dict(rule_description = description,port=port,protocol='udp')
            vap.add_app_port_mapping_rule(self.zdcli,[dict1],True)
            del dict1

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'port_mapping_cfg':[],
                     'negative': False,
                     'overwrite':False,
                     'port_mapping_num':0,}#max num is 1024
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
