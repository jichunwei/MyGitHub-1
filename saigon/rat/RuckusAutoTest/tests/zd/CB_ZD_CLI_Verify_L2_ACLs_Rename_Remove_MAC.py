'''
Created on Jan 28, 2011
@author: louis.lou@ruckuswireless.com
description:

'''
import logging
import random

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zdcli import l2_acl_cli

from RuckusAutoTest.components import Helper_ZD as zhlp


class CB_ZD_CLI_Verify_L2_ACLs_Rename_Remove_MAC(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        edit_l2acl_conf = random.choice(self.l2acl_conf_list)
        mac = edit_l2acl_conf['mac_entries'][0]
        edit_l2acl_conf.update(dict(new_name = 'new-name' + utils.make_random_string(random.randint(2,24),type = 'alnum')))
        l2_acl_cli._remove_mac_addr_from_l2acl(self.zdcli, edit_l2acl_conf['acl_name'], mac) 
        l2_acl_cli._rename_l2acl(self.zdcli, edit_l2acl_conf)  
        
        cli_get = l2_acl_cli.show_l2acl_name(self.zdcli, edit_l2acl_conf['new_name'])
        
        
        id = cli_get['L2/MAC ACL']['ID'].keys()[0]
        
        cli_get_dict = cli_get['L2/MAC ACL']['ID'][id]
        
        if cli_get_dict['Name'] != edit_l2acl_conf['new_name']:
            self.errmsg = "L2 ACL name not renamed"
        #@author: Liang Aihua, @change: Add conditions for only one mac address in acl list(2014-11-18) 
        if cli_get_dict.has_key('Stations'): 
            if edit_l2acl_conf['mac_entries'][0] in cli_get_dict['Stations']['MAC Address']:
                self.errmsg = "L2 ACL MAC[%s] are not removed" % edit_l2acl_conf['mac_entries'][0]
        #if edit_l2acl_conf['mac_entries'][0]!= cli_get_dict['Stations']['MAC Address']:
        #    self.errmsg = "L2 ACL MAC[%s] are not removed" % edit_l2acl_conf['mac_entries'][0]    
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
                         l2acl_conf_list = conf['l2acl_conf_list']
                         )
        
        self.conf.update(conf)
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.l2acl_conf_list = self.conf['l2acl_conf_list']
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         