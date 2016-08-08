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
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod

class CB_ZD_Station_Execute_ZeroIT(Test):
    def config(self, conf):
        self._init_test_parameters(conf)
        self._retrieve_carrier_bag()

    def test(self):
        try:
            if self.conf['is_restart_adapter']:
                tmethod.restart_station_adapter(self.target_station)
            self._execute_zero_it()
        except Exception, ex:
            self. errmsg = ex.message
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = 'Associate station [%s] successfully via Zero IT.' % self.conf['sta_tag']
            return self.returnResult('PASS', self.passmsg)
        
    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        
        self.conf = {'check_status_timeout': 120,
                     'is_negative': False,
                     'is_restart_adapter': False,
                     'wlan_cfg': {},
                     'sta_tag': '',
                     }
        self.conf.update(conf)
        
        self.wlan_cfg = self.conf['wlan_cfg']
        self.check_status_timeout = self.conf['check_status_timeout']
        self.is_negative = self.conf['is_negative']
        
    def _retrieve_carrier_bag(self):
        self.zeroit_toolpath = self.carrierbag['zeroit_tool_path']
        self.target_station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        
    def _execute_zero_it(self):
        #Get use_raidus value via auth_svr value.
        if self.wlan_cfg.has_key('auth_svr') and not (self.wlan_cfg['auth_svr'].lower() == 'local database'):
            use_radius = True
        else:
            use_radius = False
            
        logging.info('Executing zero it to associate station to wlan %s' % self.wlan_cfg['ssid'])
        self.target_station.execute_zero_it(self.zeroit_toolpath, self.wlan_cfg['ssid'], self.wlan_cfg['auth'], use_radius)
        
        logging.info("Verify the status of the wireless adapter on the target station")
        start_time = time.time()
        self.connected = True
        while True:
            if self.target_station.get_current_status() == "connected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                errmsg = "Timed out. The station didn't associate to the WLAN after %s" % \
                             self.check_status_timeout
                logging.info(errmsg)
                self.connected = False
                self.errmsg = errmsg
                break
       
        if self.is_negative:
            #Station should not associate the wlan.
            if self.connected:
                self.errmsg = "The stations was associated although it was not allowed to."
            else:
                self.passmsg = "The stations was not associated to the wlan."
        else:
            #Station should associate the wlan.
            if self.connected:
                self.passmsg = "The stations was associated to the wlan."
            else:
                logging.info('Verify if the wlan is in the air.')
                self.errmsg = tmethod.verify_wlan_in_the_air(
                    self.target_station, self.wlan_cfg['ssid']
                )