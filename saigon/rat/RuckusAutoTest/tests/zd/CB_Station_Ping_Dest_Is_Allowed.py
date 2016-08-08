"""
Description: This script is used to verify whether the station can ping to the target ip.
Author: Jacky Luh
Email: jluh@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme

class CB_Station_Ping_Dest_Is_Allowed(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testClientPingDestIsAllowed()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        self.passmsg = 'Station [%s] ping destined ip [%s] successfully' % (self.target_station.ip_addr, self.conf['dest_ip'])     
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'ping_timeout_ms': 15 * 1000,
                     'dest_ip': '192.168.0.252',
                     'target_station': '192.168.1.11',
                     }
        self.conf.update(conf)
        try:
            self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        except:
            self.target_station = self.carrierbag['Station'][self.conf['sta_tag']]['sta_ins']
            
        self.errmsg = ''
        self.passmsg = ''

    def _testClientPingDestIsAllowed(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, 
                                                          self.conf['dest_ip'], 
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])
