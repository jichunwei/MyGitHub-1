'''
Created on 2014-06-17
@author: chen.tao@odc-ruckuswireless.com
'''
import logging
from copy import deepcopy
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import application_visibility as vap

class CB_ZD_CLI_Add_App_Denial_Policy(Test):

    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        try:
            logging.info('Start to add app denial policy via cli!')
            if self.conf['denial_policy_num']:
                self.create_specified_num_of_denial_policy(self.conf['denial_policy_num'])
            else:    
                vap.add_app_denial_policy(self.zdcli,self.conf['denial_policy_cfg'],self.conf['overwrite'])
        except: 
            self.errmsg = 'Adding app denial policy failed.'                                  
        self.passmsg = 'Adding app denial policy succeeded.'
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

    def create_specified_num_of_denial_policy(self,num):
        if num <=1 : raise Exception('Please provide a num bigger than 1')
        denial_policy_cfg = {'policy_description': 'testtest',
                             'policy_name': 'test_app_denial_policy',
                             'rules': [{'application': 'Port', 'rule_description': 11111, 'rule_id': 1},
                                       {'application': 'HTTP hostname', 'rule_description': 'google.cn', 'rule_id': 2}]}
        
        for i in range(1,num+1):
            dict1 = deepcopy(denial_policy_cfg)
            dict1['policy_description']='app_denial_policy_test_%s'%i
            dict1['policy_name']='app_denial_policy_test_%s'%i
            dict1['rules'][0]['rule_description'] = str(20000+i)
            dict1['rules'][1]['rule_description'] = 'google_test%s.cn'%i
            vap.add_app_denial_policy(self.zdcli,[dict1],True)
            del dict1

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = {'denial_policy_cfg':[],
                     'negative': False,
                     'overwrite':False,
                     'denial_policy_num':0,}#max num is 32
        self.conf.update(conf)
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
