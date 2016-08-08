"""
Description: This script is support to verify station exists on test bed
Author: Jason Lin
Email: jlin@ruckuswireless.com
"""
import libZD_TestConfig as tconfig 
from RuckusAutoTest.models import Test

class CB_ZD_Create_Station(Test):
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        self._create_target_station()
        if self.errmsg: return self.returnResult('FAIL', self.errmsg)
        self.carrierbag[self.sta_tag]['sta_ins'] = self.target_station
        self.carrierbag[self.sta_tag]['wifi_mac_addr'] = self.target_station.get_wifi_addresses()[-1]
        if self.carrierbag.has_key('station_list'):
            self.carrierbag['station_list'].append(self.target_station)
        else:
            self.carrierbag['station_list'] = []
            self.carrierbag['station_list'].append(self.target_station)
        passmsg = 'Create Station [%s %s] Successfully' % (self.sta_tag, self.sta_ip_addr)
        return self.returnResult('PASS', passmsg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.check_status_timeout=120
        self.conf = conf.copy()
        self.sta_tag = self.conf['sta_tag']
        self.sta_ip_addr = self.conf['sta_ip_addr']
        self.is_wired_sta = self.conf.get('wired_sta')
        self.carrierbag[self.sta_tag]={}

    def _create_target_station(self):
        if self.is_wired_sta:
            need_remove_wlan = False
        else:
            need_remove_wlan = True
        self.target_station = tconfig.get_target_station(self.sta_ip_addr,
                                                         self.testbed.components['Station'],
                                                         check_status_timeout = self.check_status_timeout,
                                                         remove_all_wlan = need_remove_wlan)
        if not self.target_station:
            self.errmsg = "Target station [%s %s] not found" % (self.sta_tag, self.sta_ip_addr)
