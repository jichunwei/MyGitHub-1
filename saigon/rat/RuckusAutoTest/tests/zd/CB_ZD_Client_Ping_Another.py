"""
Do the operation that one client ping another client.
Created on 2012-12-11
@author: sean.chen@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Client_Ping_Another(Test):

    def config(self, conf):
        self._init_test_params(conf)


    def test(self):
        self._test_client_ping_another()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = 'Ping test performs as expect'
            return self.returnResult('PASS', self.passmsg)


    def cleanup(self):
        pass


    def _init_test_params(self, conf):
        self.conf = {'src_sta_tag': 'sta2',
                     'dst_sta_tag': 'sta1',
                     'condition': 'allowed', #['allowed', 'disallowed']
                     'ping_timeout_ms': 10 * 1000,
                     'clean_arp_before_ping': False}
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.src_station = self.carrierbag[self.conf['src_sta_tag']]['sta_ins']
        self.dst_station = self.carrierbag[self.conf['dst_sta_tag']]['sta_ins']
        self.src_station_wifi_ip = self.carrierbag[self.conf['src_sta_tag']]['wifi_ip_addr']
        self.dst_station_wifi_ip = self.carrierbag[self.conf['dst_sta_tag']]['wifi_ip_addr']
        
    def _test_client_ping_another(self):
        if self.conf['clean_arp_before_ping']:
            try:
                self.src_station.clean_arp()
                
            except Exception, ex:
                self.errmsg = ex.message
                return
        
        if 'allowed' == self.conf['condition']:
            self.errmsg = tmethod.client_ping_dest_is_allowed(self.src_station,
                                                              self.dst_station_wifi_ip,
                                                              ping_timeout_ms = self.conf['ping_timeout_ms'])
            if self.errmsg:
                self.errmsg = tmethod.client_ping_dest_is_allowed(self.src_station,
                                                              self.dst_station_wifi_ip,
                                                              ping_timeout_ms = self.conf['ping_timeout_ms'])

        elif 'disallowed' == self.conf['condition']:
            self.errmsg = tmethod.client_ping_dest_not_allowed(self.src_station,
                                                               self.dst_station_wifi_ip,
                                                               ping_timeout_ms = self.conf['ping_timeout_ms'])

