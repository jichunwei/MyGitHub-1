'''
Created on 2013-09-23
@author: ye.songnan@odc-ruckuswireless.com
description:
    Add, edit or remove services rule.
    Verify services rule.
'''
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import bonjour_gateway as bg

class CB_ZD_CLI_Config_Services_Rule(Test):
    '''
    Add, edit, or remove services rule.
    Verify services rule.
       
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        rule_nums = bg.get_rule_nums(self.zdcli)
        
        if self.conf['tag_new']:
            (value, res) = bg.new_services_rule(self.zdcli, self.service, self.from_vlan, self.to_vlan)
            time.sleep(2)
            rule_list = bg.get_services_rule(self.zdcli)
            if self.conf['tag_nagative']:
                #if not value:#value:True means success, False means failure
                #    self.errmsg = ''
                #else:
                #    self.errmsg = 'Should add fail, but it do not.'    
                if len(rule_list) == rule_nums:
                    self.errmsg += ''
                else:
                    self.errmsg += 'Numbers of service rule should not increase.'     
            else:
                self.errmsg = res
                if len(rule_list) == rule_nums + 1:
                    self.errmsg += ''
                else:
                    self.errmsg += 'Add rule fail, numbers of service rule do not increase.'                      
            
        if self.conf['tag_edit']:
            rule_id = bg.get_services_rule_id(self.zdcli, self.service, self.from_vlan, self.to_vlan)
            (value, res) = bg.edit_services_rule(self.zdcli, self.service_changeto, self.from_vlan_changeto, self.to_vlan_changeto, rule_id)
            time.sleep(2)
            rule_list = bg.get_services_rule(self.zdcli)
            if self.conf['tag_nagative']:
                if not value:
                    self.errmsg = ''
                else:
                    self.errmsg = 'Should edit fail, but it do not.'    
                for item_dict in rule_list:
                    if (item_dict['from_vlan'], item_dict['to_vlan'], item_dict['service_name'][:30], item_dict['id']) \
                        == (self.from_vlan, self.to_vlan, self.service[:30], rule_id):
                        self.errmsg += ''
                    else:
                        self.errmsg += 'The rules should as before.'     
            else:
                self.errmsg = res
                for item_dict in rule_list:
                    if (item_dict['from_vlan'], item_dict['to_vlan'], item_dict['service_name'][:30], item_dict['id']) \
                        == (self.from_vlan_changeto, self.to_vlan_changeto, self.service_changeto[:30], rule_id):
                        self.errmsg += ''
                    else:
                        self.errmsg += 'The service rules edit fail.'                       
                          
        if self.conf['tag_del']:
            if self.conf['tag_nagative']:
                (value, res) = bg.remove_services_rule(self.zdcli, self.input_rule_id)
                time.sleep(2)
                rule_list = bg.get_services_rule(self.zdcli)
                #if not value:
                #    self.errmsg = ''
                #else:
                #    self.errmsg = 'Should delete fail, but it do not' 
                if len(rule_list) == rule_nums:
                    self.errmsg += ''
                else:
                    self.errmsg += 'Numbers of service rule should not reduce.'     
            else:
                rule_id = bg.get_services_rule_id(self.zdcli, self.service, self.from_vlan, self.to_vlan)
                (value, res) = bg.remove_services_rule(self.zdcli, rule_id)
                time.sleep(2)
                rule_list = bg.get_services_rule(self.zdcli)
                self.errmsg = res
                if len(rule_list) == rule_nums - 1:
                    self.errmsg += ''
                else:
                    self.errmsg += 'Remove rule fail, numbers of service rule do not reduce.'                      

        if self.conf.get('tag_del_all'):
            (value, res) = bg.remove_all_services_rule(self.zdcli)
            time.sleep(2)
            rule_list = bg.get_services_rule(self.zdcli)
            self.errmsg = str(res)
            if len(rule_list) == 0:
                self.errmsg += ''
            else:
                self.errmsg += 'Remove rule fail, numbers of service rule do not reduce.' 
                              
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
                         tag_new = False,
                         tag_edit = False,
                         tag_del = False,
                         tag_nagative = False,
                         note = '',
                         input_rule_id = 1
                         )
        
        self.conf.update(conf)
        
        self.service = self.conf.get('service')
        self.from_vlan = self.conf.get('from_vlan')
        self.to_vlan = self.conf.get('to_vlan')
        self.service_changeto = self.conf.get('service_changeto')
        self.from_vlan_changeto = self.conf.get('from_vlan_changeto')
        self.to_vlan_changeto = self.conf.get('to_vlan_changeto')
        self.input_rule_id = self.conf.get('input_rule_id')  
             
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass

