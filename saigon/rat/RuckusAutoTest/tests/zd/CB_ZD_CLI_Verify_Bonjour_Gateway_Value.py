'''
Created on 2013-09-22
@author: ye.songnan@odc-ruckuswireless.com
description:
    Check bonjour_gw_value is 'disabled' or 'enabled'.
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import bonjour_gateway as bg

class CB_ZD_CLI_Verify_Bonjour_Gateway_Value(Test):
    '''
    '''
    def config(self,conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        bonjour_gw_value = bg.get_bonjour_gateway_value(self.zdcli)
        if bonjour_gw_value != self.conf['bonjour_gw_value']:
            return self.returnResult('FAIL', self.errmsg)
        
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass
    

    def _init_test_params(self, conf):
        self.errmsg = 'Bonjour gateway has wrong value.'
        self.passmsg = 'Bonjour gateway has right value.'
        self.conf = dict()
        
        self.conf.update(conf)               
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        
        if self.conf.get('zdcli_tag'):
            self.zdcli=self.carrierbag[self.conf['zdcli_tag']]
    def  _retrive_carrier_bag(self):
        pass
             
    def _update_carrier_bag(self):
        pass 
    
      