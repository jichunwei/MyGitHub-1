'''
Created on 2011-2-14
@author: louis.lou@ruckuswireless.com
description:

'''
import random

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import l3_acl
from RuckusAutoTest.components.lib.zd import access_control_zd as acl

class CB_ZD_CLI_Verify_L3_ACLs_Delete_Rule(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        delete_l3acl_conf = random.choice(self.l3acl_conf_list)
        acl_name = delete_l3acl_conf['acl_name']
        rules_conf_list = delete_l3acl_conf['rule_conf_list'] 
        leng = len(rules_conf_list) + 2
        for i in range(leng,0,-1):
            l3_acl._remove_rule_order(self.zdcli, acl_name, i)
        
        l3acl_info = l3_acl.show_l3acl_name(self.zdcli, acl_name)

        if l3acl_info.has_key('Rules'):
            self.errmsg = '[ZDCLI]:There is ruler order [%s] in Rules after removing all the order via CLI' %(l3acl_info['Rules'])
        
        l3acl_info_gui = acl.get_l3_acl_policy_cfg(self.zd, acl_name)
        
        if l3acl_info_gui['rules']:
            self.errmsg = '[ZD GUI]: There is Rules order [%s] after Removing all the rule-order via CLI' % (l3acl_info_gui['rules']) 
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

     

    def _init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                         l3acl_conf_list = conf['l3acl_conf_list']
                         )
        
        self.conf.update(conf)
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.l3acl_conf_list = self.conf['l3acl_conf_list']
        
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         