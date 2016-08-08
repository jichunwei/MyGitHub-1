"""
The case is to do the operation that one wired client ping another wired client.
Created in Feb 2013
@author: sean.chen@ruckuswireless.com
"""


import logging
import random

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Eth_Client_Ping_Another(Test):

    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        self._client_ping_another()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = 'Ping test performs as expect'
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'src_sta_tag': 'sta1',
                     'dst_sta_tag': 'sta2',
                     'src_sta_ip': '192.168.0.101',
                     'dst_sta_ip': '192.168.0.102',
                     'retrieve_mtu': False,
                     'retrieve_sta_mtu': False,
                     'do_random': False,
                     'random_range': (),
                     'data_size': 1472,
                     'over_data_size': 0,
                     'disfragment': False,
                     'allow_loss': False,
                     'condition': 'allowed', #['allowed', 'disallowed']
                     'ping_timeout_ms': 20 * 1000}
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.src_station = self.carrierbag[self.conf['src_sta_tag']]['sta_ins']
        self.dst_station = self.carrierbag[self.conf['dst_sta_tag']]['sta_ins']
        if self.carrierbag[self.conf['src_sta_tag']].has_key('wifi_ip_addr'):
            self.conf['src_sta_ip'] = self.carrierbag[self.conf['src_sta_tag']]['wifi_ip_addr']
        if self.carrierbag[self.conf['dst_sta_tag']].has_key('wifi_ip_addr'):
            self.conf['dst_sta_ip'] = self.carrierbag[self.conf['dst_sta_tag']]['wifi_ip_addr']
        self.current_ap_mtu = self.carrierbag.get('current_mtu')
        self.current_sta_mtu = self.carrierbag.get('current_sta_mtu')
        
    def _client_ping_another(self):
        logging.info('Get parameters in ping')
        if self.conf['retrieve_mtu']:
            if not self.current_ap_mtu:
                self.errmsg = 'Need to retrieve AP MTU but there is no existing value'
                return
            else:
                # The data size used in ping does not contain IP header and ICMP header.
                # To get this value we can use MTU subtracting the sum of IP header and ICMP header (28 bytes).
                self.conf['data_size'] = (self.current_ap_mtu - 28)

        elif self.conf['retrieve_sta_mtu']:
            if not self.current_sta_mtu:
                self.errmsg = 'Need to retrieve station MTU but there is no existing value'
                return
            else:
                self.conf['data_size'] = (self.current_sta_mtu - 28)
        
        if self.conf['do_random']:
            if self.conf['random_range']:
                self.conf['data_size'] = random.randint(self.conf['random_range'][0], self.conf['random_range'][1])
            else:
                # The smallest MTU in Ethernet protocol is 46, then the smallest data size used in ping is 18(46 - 28).
                # Use (18 + 1) as the lower bound of the random range.
                self.conf['data_size'] = random.randint(19, (self.conf['data_size'] - 1))
        
        self.conf['data_size'] += self.conf['over_data_size']
        
        logging.info('Perform ping')
        ping_result = self.src_station.ping2(self.conf['dst_sta_ip'], 
                                             self.conf['ping_timeout_ms'], 
                                             self.conf['data_size'], 
                                             self.conf['disfragment'], 
                                             self.conf['allow_loss'])
        
        if 'allowed' == self.conf['condition']:
            if ping_result.find("Timeout") != -1:
                logging.info("Ping FAILED. Incorrect behavior")
                self.errmsg = "The target station could not send traffic, different from expected"
        
        elif 'disallowed' == self.conf['condition']:
            if ping_result.find("Timeout") == -1:
                logging.info("Ping OK. Incorrect behavior")
                self.errmsg = "The target station could send traffic, different from expected"
