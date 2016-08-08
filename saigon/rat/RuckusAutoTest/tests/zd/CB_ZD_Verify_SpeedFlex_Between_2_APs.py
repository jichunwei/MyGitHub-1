# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Sep 2010

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
   
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Run the speedflex on Mesh AP - AP1
        - Run the speedflex on eMesh AP - AP2
        - Verify if the speed difference between AP1 and AP2 is in allowed range 
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS: If the speed difference of 2 APs is in allowed range 
            FAIL:

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
import time
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Verify_SpeedFlex_Between_2_APs(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        logging.info('Get the SpeedFlex performance in AP %s' % self.ap1_info['ip_address'])
        spres1 = self._run_speedflex_on_ap(self.ap1_info)
        logging.info(pformat(spres1))
        time.sleep(30)
        
        logging.info('Get the SpeedFlex performance in AP %s' % self.ap2_info['ip_address'])
        spres2 = self._run_speedflex_on_ap(self.ap2_info)
        logging.info(pformat(spres2))
        
        logging.info('Verify the speed performance between AP[%s] and AP[%s]' % (self.ap1_info['ip_address'], 
                                                                                 self.ap2_info['ip_address']))
        
        res, msg = self._verify_speedflex_result(spres1, spres2, self.conf['allowed_diff'])
        return self.returnResult(res, msg)

    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        
        try:
            ap1_mac = self.testbed.get_ap_mac_addr_by_sym_name(conf['ap1'])
            ap2_mac = self.testbed.get_ap_mac_addr_by_sym_name(conf['ap2'])
        except:
            ap1_mac = self.carrierbag[conf['ap1']]['ap_ins'].base_mac_addr
            ap2_mac = self.carrierbag[conf['ap2']]['ap_ins'].base_mac_addr
            
        self.ap1_info = lib.zd.ap.get_ap_info_by_mac(self.zd, ap1_mac)
        self.ap2_info = lib.zd.ap.get_ap_info_by_mac(self.zd, ap2_mac)
    
    def _run_speedflex_on_ap(self, ap):
        return lib.zd.sp.run_monitor_speedflex_performance(self.zd, ap['ip_address'], ap['mac_address'])
    
    def _verify_speedflex_result(self, res1, res2, diff):
        dlink_speed_1 = float(res1['downlink']['speed'].split('Mbps')[0])
        dlink_speed_2 = float(res2['downlink']['speed'].split('Mbps')[0])
        ulink_speed_1 = float(res1['uplink']['speed'].split('Mbps')[0])
        ulink_speed_2 = float(res2['uplink']['speed'].split('Mbps')[0])
        
        dlink_diff = self._get_diff_percent(dlink_speed_1, dlink_speed_2)
        ulink_diff = self._get_diff_percent(ulink_speed_1, ulink_speed_2)
        
        if dlink_diff <= diff and ulink_diff <= diff:
            passmsg = 'The speed difference: downlink = %02f; uplink = %02f are in allowed range'
            return 'PASS', passmsg % (dlink_diff, ulink_diff)
        errmsg = "<%s, %s>" % (res1, res2) 
        errmsg += 'The max different speed is %02f. ' % diff
        if dlink_diff > diff:
            errmsg += 'The downlink speed difference is %02f. ' % dlink_diff
        if ulink_diff > diff:
            errmsg +='The uplink speed difference is %02f. ' % ulink_diff
        
        return 'FAIL', errmsg
    
    def _get_diff_percent(self, a, b):
        return (a-b)/a if a>b else (b-a)/b