'''
Created on 2010-12-6

@author: louis.lou@ruckuswireless.com
Description:
    Create Wlan list

'''

import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.lib.zd import wlan_zd
from RuckusAutoTest.components.lib.zdcli import set_wlan
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8


class CB_ZD_CLI_Create_Wlan(Test):
    '''
    Create  WLAN via CLI
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        self.errmsg = set_wlan.create_wlan(self.zdcli, self.wlan_conf)
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            if self.conf['check_wlan_timeout']:
                tmethod8.pause_test_for(self.conf['check_wlan_timeout'], "Waiting for deploy wlan configuration to AP.")
                
            self.passmsg = '[ZDCLI] Create WLAN[%s] Successfully' % self.wlan_conf['name']
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = dict(wlan_conf ={},
                         check_wlan_timeout=10,
                         )
        
        self.conf.update(conf)

        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        if self.conf.get('zdcli'):
            self.zdcli = self.carrierbag[self.conf['zdcli']]
        if self.carrierbag.has_key('wlan_conf'):
            self.wlan_conf = self.carrierbag['wlan_conf']
        else:
            self.wlan_conf = self.conf['wlan_conf']

    def _update_carrier_bag(self):
        self.carrierbag['wlan_cfg'] = self.wlan_conf
        self.carrierbag['wlan_name'] = self.wlan_conf['name']