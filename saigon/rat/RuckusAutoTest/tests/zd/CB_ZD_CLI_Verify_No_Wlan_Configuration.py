'''
Created on 2011-1-4

@author: louis.lou@ruckuswireless.com
Description:
    

'''
#import os
#import re
#import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_zd
from RuckusAutoTest.components.lib.zdcli import set_wlan


class CB_ZD_CLI_Verify_No_Wlan_Configuration(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        self.errmsg = set_wlan._verify_wlan_after_remove_cfg(self.cli_get_wlan_info)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self.errmsg = self._verify_wlan_after_remove_cfg_by_gui(self.zd,self.wlan_name)  
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

    def _verify_wlan_after_remove_cfg_by_gui(self,zd,wlan_name):
        gui_wlan_info = wlan_zd.get_wlan_conf_detail(zd, wlan_name) 
        '''
        'acc_server': u'Disabled
        'auth': 'open',
        'bgscan': 'Enabled',
        'client_isolation': 'None',
        'description': u'',
        'dvlan': 'Disabled',
        'encryption': 'none',
        'hide_ssid': 'Disabled',
        'l2acl': u'No ACLs',
        'l3acl': u'No ACLs',
        'load_balance': 'Disable
        'max_clients': u'100',
        'name': 'louis',
        'priority': 'High',
        'rate_limit_downlink': u
        'rate_limit_uplink': u'D
        'ssid': u'louis',
        'tunnel_mode': 'Disabled
        'type': 'standard-usage'
        'vlan': 'Disabled',
        'web_auth': 'Disabled',
        'zero_it': 'Disabled'}
        '''
        if gui_wlan_info['acc_server'].lower() != 'disabled':
            return ('FAIL, accounting server is not Disabled -- incorrect behaver')
    
        if gui_wlan_info['web_auth'].lower() != 'disabled':
            return('FAIL','Web Authentication is not disabled --incorrect behaver')
        
#        if gui_wlan_info['client_isolation'].lower() != 'none':
#            return ("FAIL",'Client Isolation is not None -- incorrect behaver')
        
        if gui_wlan_info['zero_it'].lower() != 'disabled':
            return('Zero-IT Activation is not Disabled--incorrect behaver')
        
        if gui_wlan_info['l2acl'].upper() != 'NO ACLS':
            return('There is L2 ACL -- incorrect behaver')
        
        if gui_wlan_info['l3acl'].upper() != 'NO ACLS':
            return('There is L3 ACL -- incorrect behaver')
        
#        if gui_wlan_info['vlan'].lower() != 'disabled':
#            return('VLAN is not disabled -- incorrect behaver')
        
        if gui_wlan_info['hide_ssid'].lower() != 'disabled':
            return('Hide SSID(Closed System) is not disabled -- incorrect behaver')
        
        if gui_wlan_info['tunnel_mode'].lower() != 'disabled':
            return('Tunnel Mode is not disabled -- incorrect behaver')
        
        if gui_wlan_info['bgscan'].lower() != 'disabled':
            return('Background Scanning is not disabled -- incorrect behaver')
        
    #    if gui_wlan_info['Load Balancing'].lower() != 'disabled':
    #        return('Load Balancing is not disabled -- incorrect behaver')
        
        if gui_wlan_info['dvlan'].lower() != 'disabled':
            return('Dynamic VLAN is not disabled -- incorrect behaver')
        
         
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = dict(
                         
                         )
        
        self.conf.update(conf)
                
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.cli_get_wlan_info = self.carrierbag['zdcli_wlan_info']
        self.wlan_name = self.carrierbag['wlan_name']
        
        
    def _update_carrier_bag(self):
        pass