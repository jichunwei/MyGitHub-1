"""
Description: This script is used to remove all wlans from the target station.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

class CB_ZD_Remove_Wlan_From_Station(Test):

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testRemoveWlanFromStation()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        self.passmsg = 'Remove all wlans from target station [%s]successfully' % self.target_station.ip_addr

        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'check_station_timeout':120, }
        self.conf.update(conf)
        if self.conf.has_key('target_station'):
            self.target_station = self.carrierbag['station_list'][self.conf['target_station']]

        else:
            self.target_station = self.carrierbag['station']

        self.errmsg = ''
        self.passmsg = ''

    def _testRemoveWlanFromStation(self):
        try:
            tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout=self.conf['check_station_timeout'])

        except Exception, e:
            self.errmsg = '[Removing wlan from target station failed] %s' % e.message

