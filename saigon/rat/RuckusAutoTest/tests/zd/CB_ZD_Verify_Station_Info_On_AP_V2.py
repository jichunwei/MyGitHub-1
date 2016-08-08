# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Aug 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
        - ssid: Wlan ssid station associated
        - sta_tag: Station tag, and will get station instance and information from carrier bag based on sta_tag
        - ap_tag: Active Point tag, and will get active point instance and information from carrier bag based on ap_tag
        
   Test procedure:
    1. Config:
        - initilize test parameters         
    2. Test:
        - Verify client information in AP side  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If client information in ap is correct 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Verify_Station_Info_On_AP_V2(Test):
    required_components = []
    parameter_description = {'ssid': 'Wlan ssid station associated',
                             'sta_tag':'Station tag, and will get station instance and information from carrier bag based on sta_tag',
                             'ap_tag':'Active Point tag, and will get active point instance and information from carrier bag based on ap_tag',}
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self._testVerifyStationInfoOnAP()
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        self.passmsg = 'Verify information of the station [%s] shown on the AP [%s] successfully' % (self.sta_wifi_mac_addr, self.active_ap.get_base_mac())      
        return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.ssid = conf['ssid']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        self.channel_no = self.carrierbag['client_info_on_zd']['channel']
        
        self.errmsg = ''
        self.passmsg = ''

    def _testVerifyStationInfoOnAP(self):
        self.errmsg = tmethod.verify_station_info_on_ap(self.active_ap, self.sta_wifi_mac_addr, self.ssid, self.channel_no)