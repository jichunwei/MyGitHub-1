# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: The case is for verifying station IP_MAC information on active AP.
   @author: Sean Chen
   @contact: sean.chen@ruckuswireless.com
   @since: Dec 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on active AP and Zone Director;
   2. Active AP object has been put into carrierbag;
   3. The wlan names of the up wlans currently has been put into carrierbag;
   4. The wifi MAC address of station has been put into carrierbag;
   5. The wifi IP address of station has been put into carrierbag.
   
   Required components: 'AP'
   Test parameters:
        - sta_tag: target station tag, the station information can bet obtained from carrierbag with sta_tag
        - ap_tag: active AP tag, created active AP object can be obtained from carrierbag with ap_tag
        - bridge: bridge interface, different bridge with different station IP_MAC information
        - expect_iptype: the IP type used in station IP_MAC information is divided to IPv4 and IPv6, 
                         '4' means IPv4, '6' means IPv6, and 'all' means both of them
        - waiting_time: check the information immediately or do that after a certain time
        - expect_exist: expect the information to exist or not
        
   Test procedure:
    1. Config:
        - Initialize test parameters, and get active AP component.         
    2. Test:
        - Verify station IP_MAC information on active AP.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If the station IP_MAC information on active AP is fully the same as expected
            FAIL: If the station IP_MAC information on active AP is not the same as expected

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging
import copy
import time

from RuckusAutoTest.models import Test

class CB_ZD_Verify_Station_IP_MAC_Info_On_AP(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._verify_sta_ip_mac_info_on_ap()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'sta_tag': 'sta1', 
                     'ap_tag': 'ap1', 
                     'bridge': 'br0', 
                     'expect_iptype': '4', 
                     'waiting_time': 0,
                     'expect_exist': True}
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.wlan_name_list = self.carrierbag['wlan_name_list']
        self.sta_wifi_mac_addr = self.carrierbag[self.conf['sta_tag']]['wifi_mac_addr']
        self.sta_wifi_ip_addr = self.carrierbag[self.conf['sta_tag']]['wifi_ip_addr']
        
    def _verify_sta_ip_mac_info_on_ap(self):
        logging.info('Verify station IP and MAC info on active AP')
        try:
            if self.conf['waiting_time']:
                logging.info(('Wait for %s seconds before verification') % self.conf['waiting_time'])
                time.sleep(self.conf['waiting_time'])
            else:
                pass
            sta_ip_mac_info = self.active_ap.get_sta_ip_mac_info(bridge = self.conf['bridge'], 
                                                                 iptype = self.conf['expect_iptype'])
            for ip_ver in sta_ip_mac_info:
                non_target_info_count = 0
                for ip_mac_info in sta_ip_mac_info[ip_ver]:
                    if (ip_mac_info.get('mac addr') == self.sta_wifi_mac_addr) and (ip_mac_info.get(ip_ver) == self.sta_wifi_ip_addr):
                        target_ip_mac_info = copy.deepcopy(ip_mac_info)
                        break
                    else:
                        non_target_info_count += 1
                if self.conf['expect_exist'] == True:
                    if non_target_info_count == len(sta_ip_mac_info[ip_ver]):
                        self.errmsg = 'There is no target station IP_MAC info on active AP in %s IP type' %(ip_ver)
                        return
                    elif target_ip_mac_info['port'] not in self.wlan_name_list:
                        self.errmsg = 'The wlan port in target station IP_MAC info on active AP is %s, not the correct one' %(target_ip_mac_info['port'])
                        return
                    self.passmsg = 'There is correct station IP and MAC info on active AP'
                else:
                    if non_target_info_count == len(sta_ip_mac_info[ip_ver]):
                        self.passmsg = 'There is no target station IP_MAC info on active AP in %s IP type, expected behavior' %(ip_ver)
                        return
                    else:
                        self.errmsg = 'There is target station IP_MAC info on active AP in %s IP type, unexpected behavior' %(ip_ver)
                        return
                    
        except Exception, ex:
            self.errmsg = ex.message
