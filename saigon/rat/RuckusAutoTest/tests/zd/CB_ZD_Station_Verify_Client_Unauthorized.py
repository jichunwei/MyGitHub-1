'''
Description:
    Make sure client is unauthorized which check from zd web ui.
Created on 2010-9-1
@author: cwang@ruckuswireless.com    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Station_Verify_Client_Unauthorized(Test):
    '''
    Make sure client is unauthorized which check from zd web ui.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
                
    def test(self):  
        # In Web authentication, when client is unauthorized, the ZD shows IP address of the client
        (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_unauthorized(
                                              self.zd,
                                              self.sta_wifi_ip_addr, self.sta_wifi_mac_addr,
                                              self.check_status_timeout)    
            
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        self.passmsg = 'Client authenticate successfully, detail [%s]' % self.client_info
        
        logging.info(self.passmsg)
        self._update_carrier_bag()                              
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('station'):
            self.target_station = self.carrierbag['station']
            self.sta_wifi_ip_addr = self.carrierbag['sta_wifi_ip_addr']
            self.sta_wifi_mac_addr = self.carrierbag['sta_wifi_mac_addr']
        elif self.carrierbag.has_key(self.conf['sta_tag']):
            self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
            self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
            self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        else:
            pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(check_status_timeout = 360)
        self.conf.update(conf)
        self.check_status_timeout = self.conf['check_status_timeout']        
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
            