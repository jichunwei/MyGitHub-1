"""
Description: This script is used to configure a WLAN on the target station and check association status of the target station.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from copy import deepcopy


class CB_ZD_Associate_Station(Test):

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testAssociateStationWithSSID()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        self.passmsg = 'Associate station [%s] successfully' % self.target_station.ip_addr
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'check_status_timeout':120,}
        self.conf.update(conf)
        self.wlan_cfg = conf['wlan_cfg']
        if self.conf.has_key("target_station"):
            self.target_station = self.carrierbag['station_list'][self.conf['target_station']]

        else:
            self.target_station = self.carrierbag['station']

        self.errmsg = ''
        self.passmsg = ''

    def _testAssociateStationWithSSID(self):
        wlan_cfg = deepcopy(self.wlan_cfg)
        if self.wlan_cfg.has_key("wpa_ver") and self.wlan_cfg['wpa_ver'] == "WPA_Mixed":
            wlan_cfg['wpa_ver'] = wlan_cfg['sta_wpa_ver']
            wlan_cfg['encryption'] = wlan_cfg['sta_encryption']

        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station, wlan_cfg, self.conf['check_status_timeout'])
        if self.errmsg:
            self.errmsg = tmethod.verify_wlan_in_the_air(self.target_station, wlan_cfg['ssid'])
