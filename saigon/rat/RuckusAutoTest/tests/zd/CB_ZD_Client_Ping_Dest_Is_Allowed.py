"""
Description: This script is used to verify whether the station can ping to the target ip.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Client_Ping_Dest_Is_Allowed(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testClientPingDestIsAllowed()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        self.passmsg = 'Station [%s] ping destined ip [%s] successfully' % (self.target_station.ip_addr, self.conf['target_ip'])     
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'ping_timeout_ms': 15 * 1000,
                     'target_ip': '192.168.0.252',
                     }
        self.conf.update(conf)
        self.target_station = self.carrierbag['station']
        self.errmsg = ''
        self.passmsg = ''

    def _testClientPingDestIsAllowed(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, 
                                                          self.conf['target_ip'], 
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])
