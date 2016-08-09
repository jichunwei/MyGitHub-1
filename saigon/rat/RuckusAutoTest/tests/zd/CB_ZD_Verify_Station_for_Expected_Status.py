'''
Created on Jan 24, 2014

@author: jacky luh
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Verify_Station_for_Expected_Status(Test):
    '''
    Make sure client is unauthorized which check from zd web ui.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

             
    def test(self):  
        # In Web authentication, when client is unauthorized, the ZD shows IP address of the client
        if self.status == 'unauthorized':
            (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_unauthorized(
                                                  self.zd,
                                                  self.sta_wifi_ip_addr, self.sta_wifi_mac_addr,
                                                  self.check_status_timeout)
            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)
            self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.conf['dest_ip'], 
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])
            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)     
        elif self.status == 'authorized':
            #JLUH@20140424, modified by the guest auth authorized status
            if self.full_name:
                self.sta_wifi_ip_addr = self.full_name
            (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_authorized(self.zd,
                                                                                     self.sta_wifi_ip_addr, self.sta_wifi_mac_addr,
                                                                                     self.check_status_timeout)
            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)
            
            self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.conf['dest_ip'])
            if self.errmsg:
                return self.returnResult("FAIL", self.errmsg)
              
        self.passmsg = 'Client authenticate successfully, detail [%s]' % self.client_info
        
        logging.info(self.passmsg)
        self._update_carrier_bag()                              
        return self.returnResult("PASS", self.passmsg)

   
    def cleanup(self):
        pass


    def _retrive_carrier_bag(self):
        if self.carrierbag.get('guest_fullname'):
            self.full_name = self.carrierbag['guest_fullname']
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
        self.conf = {'check_status_timeout': 360,
                     'ping_timeout_ms': 15*1000,
                     #'dest_ip': '192.168.0.252',
                     'dest_ip': '172.126.0.252',
                     'sta_tag': '192.168.1.11'}
        self.conf.update(conf)
        self.status = self.conf['status']
        self.check_status_timeout = self.conf['check_status_timeout']        
        self.zd = self.testbed.components['ZoneDirector']
        self.target_station = self.carrierbag['station']
        self.errmsg = ''
        self.passmsg = ''
            