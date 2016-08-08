'''
Description:

Created on 2010-9-1
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Station_Verify_Client_Authorized(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self._update_carrier_bag()

        # In Web authentication, after the client is authorized, the ZD shows username used to authenticate of the client
        (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_authorized(
                                              self.zd,
                                              self.username, self.sta_wifi_mac_addr,
                                              self.check_status_timeout)    
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        
        self.passmsg = "Client check successfully, detail [%s]" % self.client_info
        logging.info(self.passmsg)
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('station'):
            self.sta_wifi_mac_addr = self.carrierbag['sta_wifi_mac_addr']
        elif self.carrierbag.has_key(self.conf['sta_tag']):
            self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        else:
            pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(username = 'ras.local.user',
                         check_status_timeout = 360)
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.username = self.conf['username']
        self.check_status_timeout = self.conf['check_status_timeout']
        self.errmsg = ''
        self.passmsg = ''
        
        
    
    
