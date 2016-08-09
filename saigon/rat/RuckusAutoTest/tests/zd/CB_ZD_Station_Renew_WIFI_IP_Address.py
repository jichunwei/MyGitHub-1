'''
Description:
Created on 2010-9-1
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Station_Renew_WIFI_IP_Address(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self._renew_wifi()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
             
        self._update_carrier_bag()        
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.target_station = self.carrierbag['station']
    
    def _update_carrier_bag(self):
        self.carrierbag['sta_wifi_ip_addr'] = self.sta_wifi_ip_addr
        self.carrierbag['sta_wifi_mac_addr'] = self.sta_wifi_mac_addr
    
    def _init_test_params(self, conf):
        self.conf = dict(check_status_timeout = 360)
        self.conf.update(conf)
        self.check_status_timeout = 360
        self.errmsg = ''
        self.passmsg = ''
    
    def _renew_wifi(self):
        (self.anOK, self.sta_wifi_ip_addr, self.sta_wifi_mac_addr) = \
        (self.anOK, self.xtype, self.errmsg) = \
            tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)
        # we use self.errmsg to indicate method PASS or FAIL; so set to '' if everything is an OK
        if self.anOK:
            self.errmsg = ''
            return self.errmsg        
        elif self.xtype == 'FAIL':
            return self.errmsg
        else:
            raise Exception(self.errmsg)     