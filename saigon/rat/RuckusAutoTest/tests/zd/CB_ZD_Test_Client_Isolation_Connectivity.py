"""
Description: This script is used to verify whether the station can ping to the target ip.
Author: Toan Trieu
Email: tntoan@s3solutions.com.vn
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Test_Client_Isolation_Connectivity(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)
        self._get_target_ip()
        
    def test(self):
        if self.conf['isolation_option'] == "none":
            self._testClientPingDestIsAllowed()
        else: 
            self._testClientPingDestNotAllowed()
            
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)

        if self.conf['isolation_option'] == "none":
            self.passmsg = 'Station [%s] ping destined ip [%s] successfully' % (self.target_station, self.conf['target_ip'])
        else:
            self.passmsg = 'Station [%s] ping destined ip [%s] failed, correct behavior' % (self.target_station, self.conf['target_ip'])

        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'ping_timeout_ms': 150 * 1000,
                     'source_station': 0,
                     'target_station': 1,
                     'target_ip': '',
                     'isolation_option': '',
                     'check_status_timeout': 180,
                     }
        self.conf.update(conf)
        self.source_station = self.carrierbag['station_list'][self.conf['source_station']]
        self.target_station = self.carrierbag['station_list'][self.conf['target_station']]
        self.errmsg = ''
        self.passmsg = ''
        
    def _get_target_ip(self):
        res, wifi_ip_addr, wifi_mac_addr = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
    
        if not res:
            raise Exception(wifi_mac_addr)   
        
        self.conf['target_ip'] =  wifi_ip_addr    

    def _testClientPingDestNotAllowed(self):
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.source_station, 
                                                          self.conf['target_ip'], 
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])
        
    def _testClientPingDestIsAllowed(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.source_station, 
                                                          self.conf['target_ip'], 
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])        