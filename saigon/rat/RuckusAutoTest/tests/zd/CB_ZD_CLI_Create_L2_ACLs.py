'''
Created on Jan 28, 2011
@author: louis.lou@ruckuswireless.com
description:

'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import l2_acl_cli

from RuckusAutoTest.components import Helper_ZD as zhlp


class CB_ZD_CLI_Create_L2_ACLs(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        l2_acl_cli.create_l2acl(self.zdcli, self.l2acl_conf_list)
         
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
                         l2acl_conf_list = [],
                         sta_tag = '', #@author: Jane.Guo @since: 2013-8-6 add station mac
                         )
        self.conf.update(conf)
        self.l2acl_conf_list = self.conf['l2acl_conf_list']  
        if self.conf.get('sta_tag'):
            target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
            target_station_mac = target_station.get_wifi_addresses()[1]
            self.l2acl_conf_list[0]['mac_entries'].append(target_station_mac)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass         