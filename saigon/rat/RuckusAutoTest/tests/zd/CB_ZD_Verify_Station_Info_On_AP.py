"""
Description: This script is used to verify the information of the station shown on the active AP.
Author: Serena Tan
Email: serena.tan@ruckuswireless.com
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod


class CB_ZD_Verify_Station_Info_On_AP(Test):
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testVerifyStationInfoOnAP()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        passmsg = 'Verify information of the station [%s] shown on the AP [%s] successfully'
        self.passmsg = passmsg % (self.sta_wifi_mac_addr, self.active_ap.get_base_mac())      
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.ssid = conf['ssid']
        if conf.get('sta_tag'):
            self.sta_wifi_mac_addr = self.carrierbag[conf['sta_tag']]['wifi_mac_addr']
        
        else:
            self.sta_wifi_mac_addr = self.carrierbag['sta_wifi_mac_addr']
        
        if conf.get('ap_tag'):
            self.active_ap = self.carrierbag[conf['ap_tag']]['ap_ins']
        
        else:
            self.active_ap = self.carrierbag['active_ap']['AP1']
            
        self.channel_no = self.carrierbag['client_info_on_zd']['channel']
        self.errmsg = ''
        self.passmsg = ''

    def _testVerifyStationInfoOnAP(self):
        self.errmsg = tmethod.verify_station_info_on_ap(self.active_ap, 
                                                        self.sta_wifi_mac_addr, 
                                                        self.ssid, 
                                                        self.channel_no)
        