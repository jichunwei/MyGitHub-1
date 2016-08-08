"""
Description: This script is used to verify whether the station can ping to the target ip.
Author: Jacky Luh
Email: jluh@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_Station_Ping_Dest_Is_Denied(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._test_client_ping_dest_is_denied()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        self.passmsg = 'Station [%s] can not ping pass destined ip [%s]. Correct behavior' % (self.target_station.ip_addr, self.conf['dest_ip'])     
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'ping_timeout_ms': 15 * 1000,
                     'dest_ip': '192.168.0.252',
                     'sta_tag': '192.168.1.11',
                     'clean_arp_before_ping':False,
                     }
        self.conf.update(conf)
        try:
            self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        except:
            self.target_station = self.carrierbag['Station'][self.conf['sta_tag']]['sta_ins']
        self.errmsg = ''
        self.passmsg = ''

    def _test_client_ping_dest_is_denied(self):
        if self.conf['clean_arp_before_ping']:
            try:
                self.target_station.clean_arp()
                
            except Exception, ex:
                self.errmsg = ex.message
                return
        
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.conf['dest_ip'], 
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])
