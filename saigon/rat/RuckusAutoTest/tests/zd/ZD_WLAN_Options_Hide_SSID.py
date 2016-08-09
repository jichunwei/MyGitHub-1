# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_WLAN_Options_Hide_SSID verify Hide SSID settings option on Zone Director. 

Product Line: ZoneFlex

Test_bed_type
    ZoneDirector Test Bed

References

Test_ID/Customer_bug_ID
-   ZD_Hide_BSSID

Pre-requisite
- 

Configuration and Parameters
- 'active_ap': AP symbolic name or mac address (XX:XX:XX:XX:XX:XX)of target ap which used to test hide BSSID
- 'target_station': ip address of target station
- 'test_option': hide ssid/ show ssid/ specific ap

Example parameters: 
{'active_ap': 'AP_01', 'target_station': '192.168.1.10', 'test_option': 'hide ssid'}

Test Procedure
1. Configure wlan using input parameters. 
2. if 'use_hide_ssid' is True, SSID must not be broadcast in beacons

Observable Results
- 

Pass/Fail Criteria (including pass/fail messages)
 FAIL: 
 - 'use_hide_ssid' is True and client see SSID is broadcast in beacons
 - 'use_hide_ssid' is False and client can't find SSID in beacons
 PASS:
 - 'use_hide_ssid' is True and client can't find SSID is broadcast in beacons
 - 'use_hide_ssid' is False and client find SSID in beacons

How it was tested:

"""

import os
import re
import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_WLAN_Options_Hide_SSID(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_station':'ip address of target station',
                           'active_ap':'AP symbolic name or MAC address (XX:XX:XX:XX:XX:XX)of target ap',
                           'test_option': 'hide ssid/ show ssid/ specific ap'}

    def config(self, conf):
        # Define test parameters
        self._initTestParams(conf)
        # Repair the target station for the testing
        self._cfgTargetStation()
        # Repair the Zone Director for the testing
        self._cfgZoneDirector()

    def test(self):
        result, msg = ["", ""]
        
        # set run_times = 2 to run both enable & disable Hide BSSID in 1 test case
        # run_times =1, only run with either BSSID enabled or BSSID disabled
        if not self.wlan_cfg.has_key('use_hide_ssid'):
            self.wlan_cfg['use_hide_ssid'] = True
            run_times = 2
        else:
            run_times = 1
        
        while run_times > 0:
            logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
            self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan_cfg)
            # Wait a moment for ZD to push config to APs
            time.sleep(10)
    
            # Determine DUT AP (active_ap)
            # and turn-off wlan on non-active AP to ensure wireless client only associate to DUT AP
            self._cfgActiveAPs()
    
            # try to find ssid broadcast or not
            logging.debug("Verifying with Hide SSID option %s" % self.wlan_cfg['use_hide_ssid'])
            find_ssid = self.target_station.check_ssid(self.wlan_cfg['ssid'])
            start_time = time.time()
            current_time = start_time
            while current_time - start_time <= self.check_status_timeout:
                if find_ssid and self.wlan_cfg['use_hide_ssid']:
                    result, msg = ("FAIL", "AP broadcast SSID in beacons while Hide BSSID is enabled")
                    break
                elif find_ssid and not self.wlan_cfg['use_hide_ssid']:
                    result, msg = ("PASS", "")
                    break
                            
                time.sleep(1)
                find_ssid = self.target_station.check_ssid(self.wlan_cfg['ssid'])
                current_time = time.time()     
    
            # after timeout return FAIL if Hide BSSID is not enable and can't find SSID is broadcast in beacon
            if not find_ssid and not self.wlan_cfg['use_hide_ssid']:
                result, msg = ("FAIL", "Can't find SSID is broadcast in beacon while Hide BSSID is disabled")
                break
            else:
                result, msg = ("PASS", "") 
                           
            if run_times == 2:
                # retest with Hide SSID disabled for that AP
                self.wlan_cfg['use_hide_ssid'] = False
                self.testbed.components['ZoneDirector'].remove_wlan(self.wlan_cfg)
                
            run_times -= 1

        return (result, msg)
    
    def cleanup(self):
        logging.info("Remove all the WLANs on the Zone Director")
        #self.testbed.components['ZoneDirector'].remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

    def _initTestParams(self, conf):
        # Testing parameters
        self.target_station = None
        self.conf = conf
        self.ping_timeout = 150
        self.check_status_timeout = 120
        ssid = "rat-hide-bssid-%s" % time.strftime("%H%M%S")
        self.wlan_cfg = {'username': '', 'ssid': ssid, 'ras_port': '', 'key_string': '',
                         'key_index': '', 'auth': 'open', 'ras_secret': '', 'use_radius': False,
                         'encryption': 'none', 'ras_addr': '', 'password': 'ras.eap.user', 'wpa_ver': ''}
        if conf['test_option'] == 'hide ssid':
            self.wlan_cfg['use_hide_ssid'] = True
        if conf['test_option'] == 'show ssid':
            self.wlan_cfg['use_hide_ssid'] = False

    def _cfgTargetStation(self):
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.check_status_timeout
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgActiveAPs(self):
        # Get the Actice APs and disable all wlan interface (non mesh interface) in non active aps
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            print self.active_ap.ip_addr
            if self.active_ap:
                for ap in self.testbed.components['AP']:
                    if ap is not self.active_ap:
                        logging.info("Remove all WLAN on non-active AP %s" % ap.get_base_mac())
                        ap.remove_all_wlan()

                logging.info("Verify WLAN status on the active AP %s" % self.active_ap.get_base_mac())
                if not self.active_ap.verify_wlan():
                    return ("FAIL", "WLAN %s on active AP %s is not up" % (self.active_ap.ssid_to_wlan_if(self.wlan_cfg['ssid']),
                                                                           self.active_ap.get_base_mac()))
                    
            else:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])

    def _cfgZoneDirector(self):
        logging.info("Remove all wlan configuration on the Zone Director")
        self.testbed.components['ZoneDirector'].remove_all_wlan()
