# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Nov 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Station'
   Test parameters:
       - check_status_timeout: timeout for check status,
       - expected_subnet: Station expected subnet for ipv4. E.g. 192.168.0.0/255.255.255.0
       - expected_subnet_ipv6: Station expected subnet for ipv6.E.g. 2020:db8:1::251/64
        
   Test procedure:
    1. Config:
        - initilize test parameters         
    2. Test:
        - Get station wifi ipv4 and ipv6 address
        - Verify ipv4 and ipv6 address are in expected subnet.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Get station wifi address successfully and they are in expected subnet. 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.common import lib_Constant as const
from RuckusAutoTest.models import Test

class CB_ZD_Station_Download_ZeroIT(Test):
    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        try:
            self._download_zero_it()
        except Exception, ex:
            self. errmsg = ex.message
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)
        
    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = {'sta_tag': '',
                     'wlan_cfg': ''}
        self.conf.update(conf)
        
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.zd = self.testbed.components['ZoneDirector']
        
        self.wlan_cfg = self.conf['wlan_cfg']
        
        self.activate_url = self.zd.get_zero_it_activate_url()
        
    def _update_carrier_bag(self):
        self.carrierbag['zeroit_tool_path'] = self.zeroit_tool_path

    def _download_zero_it(self):
        logging.info('Download Zero-IT application to station')
        ip_type = const.IPV6        
        self.zeroit_tool_path = self.target_station.download_zero_it(None, None, None, self.activate_url, self.wlan_cfg['username'], self.wlan_cfg['password'], ip_type)
        
        self.passmsg = 'Download Zero-IT application to %s successfully on %s.' % (self.zeroit_tool_path, self.conf['sta_tag'])         
        
    