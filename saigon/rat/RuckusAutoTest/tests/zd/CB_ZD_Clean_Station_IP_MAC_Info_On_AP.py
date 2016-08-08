# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: The case is for cleaning station IP_MAC information on active AP.
   @author: Sean Chen
   @contact: sean.chen@ruckuswireless.com
   @since: Dec 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on active AP and Zone Director;
   2. Active AP object has been put into carrierbag;
   3. The wlan names of the up wlans currently has been put into carrierbag;
   4. The wifi MAC address of station has been put into carrierbag.
   
   Required components: 'AP'
   Test parameters:
        - sta_tag: target station tag, the station information can bet obtained from carrierbag with sta_tag
        - ap_tag: active AP tag, created active AP object can be obtained from carrierbag with ap_tag
        - bridge: bridge interface, different bridge with different station IP_MAC information
        - expect_iptype: the IP type used in station IP_MAC information is divided to IPv4 and IPv6, 
                         '4' means IPv4, '6' means IPv6, and 'all' means both of them
        
   Test procedure:
    1. Config:
        - Initialize test parameters, and get active AP component.         
    2. Test:
        - Clean station IP_MAC information on active AP.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If the cleaning operation can be implemented without any error
            FAIL: If any error happens during the operation

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging
import time

from RuckusAutoTest.models import Test

class CB_ZD_Clean_Station_IP_MAC_Info_On_AP(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._clean_sta_ip_mac_info_on_ap()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'sta_tag': 'sta1', 'ap_tag': 'ap1', 'bridge': 'br0', 'expect_iptype': '4'}
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.wlan_name_list = self.carrierbag['wlan_name_list']
        self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']

    def _clean_sta_ip_mac_info_on_ap(self):
        logging.info('Clean station IP and MAC info on active AP')
        try:
            del_count = 0
            while(del_count < 3):
                for wlan_name in self.wlan_name_list:
                    self.active_ap.del_sta_ip_mac_info(bridge = self.conf['bridge'], 
                                                  wlan_port = wlan_name, 
                                                  sta_wifi_mac = self.sta_wifi_mac_addr, 
                                                  iptype = self.conf['expect_iptype'])
                del_count += 1
                time.sleep(2)
            
            self.passmsg = 'Clean station IP and MAC info on active AP successfully'
            
        except Exception, ex:
            self.errmsg = ex.message
 