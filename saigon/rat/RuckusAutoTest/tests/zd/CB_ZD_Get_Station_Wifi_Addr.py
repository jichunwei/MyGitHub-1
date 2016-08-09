"""
Description: This script is used to get the wifi ip address and mac address of the target station.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Get_Station_Wifi_Addr(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testVerifyStationInfoOnZD()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        self._updateCarrierBag()
        self.passmsg = 'Get station wifi ip address [%s] and wifi mac address [%s] successfully' % (self.var1, self.var2.lower())      
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'check_status_timeout':120,}
        self.conf.update(conf)
        if self.conf.has_key("target_station"):
            self.target_station = self.carrierbag['station_list'][self.conf['target_station']]
        else:    
            self.target_station = self.carrierbag['station']    
        self.errmsg = ''
        self.passmsg = ''

    def _testVerifyStationInfoOnZD(self):
        res, self.var1, self.var2 = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
        if not res:
            self.errmsg = self.var2
        
    def _updateCarrierBag(self):
        self.carrierbag['sta_wifi_ip_addr'] = self.var1
        self.carrierbag['sta_wifi_mac_addr'] = self.var2.lower()
