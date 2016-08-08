# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: The case is for verifying wlan Proxy APR status on active AP.
   @author: Sean Chen
   @contact: sean.chen@ruckuswireless.com
   @since: Nov 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on active AP and Zone Director;
   2. Active AP object has been put into carrierbag;
   3. The target wlan names has been put into the test configuration or carrierbag.
   
   Required components: 'AP'
   Test parameters:
        - ap_tag: active AP tag, created active AP object can be obtained from carrierbag with ap_tag
        - bridge: bridge interface, different bridge with different proxy arp information
        - wlan_name_list: the names of the wlan interfaces to check the proxy arp information at
        - expected_status: the proxy arp status expected to be
        
   Test procedure:
    1. Config:
        - Initialize test parameters, and get active AP component.         
    2. Test:
        - Verify wlan Proxy APR status on active AP.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If the target wlan Proxy APR status on active AP is same as expect
            FAIL: If the target wlan info doesn't exist or the status is not the same as expected

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging
import time

from RuckusAutoTest.models import Test

class CB_ZD_Verify_WLAN_Proxy_ARP_On_AP(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._verify_wlan_proxy_arp_on_ap()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrierbag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'ap_tag': 'ap1', 
                     'bridge': 'br0', 
                     'wlan_name_list': [], 
                     'waiting_time': 0,
                     'expected_status': 'n'}
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        if self.conf['wlan_name_list']:
            self.wlan_name_list = self.conf['wlan_name_list']
        else:
            self.wlan_name_list = self.carrierbag['wlan_name_list']

    def _verify_wlan_proxy_arp_on_ap(self):
        logging.info('Verify WLAN PIF Service status on active AP')
        if self.conf['waiting_time']:
            logging.info(('Wait for %s seconds before verification') % self.conf['waiting_time'])
            time.sleep(self.conf['waiting_time'])
        else:
            pass
        br_info = self.active_ap.get_bridge_setting(bridge = self.conf['bridge'])
        br_port_name_match_count = 0
        for br_port_info in br_info:
            if br_port_info['Port'] in self.wlan_name_list:
                br_port_name_match_count += 1
                if self.conf['expected_status'] != br_port_info['Serv']:
                    self.errmsg = 'The PIF Service status of %s on active AP is %s instead of %s' % (br_port_info['Port'], br_port_info['Serv'], self.conf['expected_status'])
                    return
        if br_port_name_match_count == 0:
            self.errmsg = 'There are no created wlan interfaces shown in the active AP bridge info'
            return
        elif br_port_name_match_count < len(self.wlan_name_list):
            self.errmsg = 'The target wlan interfaces are not all shown in the active AP bridge info'
            return
        else:
            self.passmsg = 'The wlan PIF Service status on active AP is correct as %s' % (self.conf['expected_status'])
        
    def _update_carrierbag(self):
        pass
