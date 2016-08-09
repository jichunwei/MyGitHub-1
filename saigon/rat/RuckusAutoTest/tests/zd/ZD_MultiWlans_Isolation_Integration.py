# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script is use to test 32 WLANs integration with the 'Wireless Clients Isolation' option.
             The test support test on mesh test bed, with out changing the test bed topology.
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'target_station_1': IP address of the target station 1
                    'target_station_2': IP address of the target station 2
                    'active_ap': the AP symbolic name of the active AP. It is the Mesh AP or Root AP
                    'wlan_config_set': list of 32 WLAN configurations will be test.
                                       Default is list of 32 WLANs with "Open - None" encryption.

   Result type: PASS/FAIL/ERROR
   Results:    FAIL:  If any of the above criteria is not satisfied.
               PASS:  If all verify steps are successfully.
   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
        - Create 32 WLANs on the Zone Director base on the 'wlan_config_set'parameter.
   2. Test:
        - Enable 'Wireless Clients Isolation' option o Zone Director
        - Assign sequence 32 WLANs to Default group and verify:
            a.    2 target stations could access to the network and get the correct IP address.
            b.    2 target stations could not ping to each other.
   3. Cleanup:
        - Return all non-default setting on Zone Director

   How it is tested?

"""

import os
import re
import logging
import time

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class ZD_MultiWlans_Isolation_Integration(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    test_parameters = {'target_station_1': 'IP address of the target station 1',
                       'target_station_2': 'IP address of the target station 2',
                       'active_ap': 'the AP symbolic name of the active AP. It is the Mesh AP or Root AP',
                       'wlan_config_set': 'list of 32 WLAN configurations will be test'}

    def config(self, conf):
        self._initTestParameter(conf)
        self._cfgZoneDirector()
        self._cfgTargetStation()
        self._cfgActiveAP()

    def test(self):
        # Verify if the Isolation behavior is correct on all wlans
        self._verifyIsolationBehavioronAllWlans()

        if self.errmsg: return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #lib.zd.wlan.delete_all_wlans(self.zd)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        # Remove all wlan profiles on target station
        if self.target_station_1:
            self.target_station_1.remove_all_wlan()

        if self.target_station_2:
            self.target_station_2.remove_all_wlan()

    def _initTestParameter(self, conf):
        self.conf = {'target_station_1':'',
                     'target_station_2':'',
                     'active_ap':'',
                     'wlan_config_set':'set_of_32_open_none_wlans', 
                     'tested_wlan_list': []}
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.target_station_1 = None
        self.target_station_2 = None

        self.wlan_conf_list = tconfig.get_wlan_profile(self.conf['wlan_config_set'])
        for wlan in self.wlan_conf_list:
            wlan.update({'do_isolation': True})
        self.wlan_name_list = [wlan['ssid'] for wlan in self.wlan_conf_list]
        self.check_status_timeout = 180
        self.negative_check_status_timeout = 20
        self.break_time = 2
        self.test_wlan_number = 6
        self.errmsg = ''
        self.passmsg = ''

    def _cfgTargetStation(self):
        self.target_station_1 = tconfig.get_target_station(self.conf['target_station_1']
                                                         , self.testbed.components['Station']
                                                         , check_status_timeout = self.check_status_timeout
                                                         , remove_all_wlan = True)
        if not self.target_station_1:
            raise Exception("Target station %s not found" % self.conf['target_station_1'])

        self.target_station_2 = tconfig.get_target_station(self.conf['target_station_2']
                                                         , self.testbed.components['Station']
                                                         , check_status_timeout = self.check_status_timeout
                                                         , remove_all_wlan = True)
        if not self.target_station_2:
            raise Exception("Target station %s not found" % self.conf['target_station_2'])

    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #lib.zd.wlan.delete_all_wlans(self.zd)

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        # Create wlans set for testing
        lib.zd.wlan.create_multi_wlans(self.zd, self.wlan_conf_list)   
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')
    
    def _cfgActiveAP(self):        
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])
            self.active_ap_mac = self.active_ap.get_base_mac().lower()

    def _remove_all_wlanOnNonActiveAPs(self):
        if self.active_ap:
            for ap in self.testbed.components['AP']:
                if ap is not self.active_ap:
                    logging.info("Remove all WLAN on non-active AP %s" % ap.ip_addr)
                    ap.remove_all_wlan()

            logging.info("Verify WLAN status on the active AP %s" % self.active_ap.ip_addr)
            if not self.active_ap.verify_wlan():
                raise Exception('Not all wlan are up on active AP %s' % self.active_ap.ip_addr)

    def _verifyIsolationBehavioronAllWlans(self):
        error_at_wlan = []
        # Remove all wlan members out of Default group
        lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default', self.wlan_name_list, False)
        last_asigned_wlans = []
        logging.info('Verify on wlans %s' % self.conf['tested_wlan_list'])
        verify_wlan_conf_list = []
        for i in self.conf['tested_wlan_list']:                
            verify_wlan_conf_list.append(self.wlan_conf_list[i])
                    
        # Remove all assigned wlans out of Default group
        if last_asigned_wlans:
            lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default', last_asigned_wlans, False)
        # Apply the selected wlans to Default group for testing
        verify_wlan_name_list = [wlan['ssid'] for wlan in verify_wlan_conf_list]
        lib.zd.wgs.cfg_wlan_group_members(self.zd, 'Default', verify_wlan_name_list, True)
        last_asigned_wlans = verify_wlan_name_list

        val = self._verifyActiveStationsCouldNotReachToEachOther(verify_wlan_conf_list)
        error_at_wlan.extend(val)

        if error_at_wlan:
            self.errmsg = 'The Isolation Option did not work well on wlans %s' % str(error_at_wlan)
        else:
            self.passmsg = 'The Isolation Option worked well on %d wlans' % len(self.wlan_conf_list)

    def _verifyActiveStationsCouldNotReachToEachOther(self, wlan_conf_list):
        # Verify clients could access to the wlans but could not ping to each other
        error_at_wlan = []
        for wlan in wlan_conf_list:
            sta1_wifi_ip_addr = ''
            sta2_wifi_ip_addr = ''
            logging.info('Verify Wireless Client Isolation Option on wlan %s [%s]' % (wlan['ssid'], str(wlan)))

            sta1_wifi_ip_addr = self._checkStationAssociation(self.target_station_1, wlan)
            sta2_wifi_ip_addr = self._checkStationAssociation(self.target_station_2, wlan)

            errmsg1 = tmethod.client_ping_dest_not_allowed(self.target_station_1, sta2_wifi_ip_addr)
            errmsg2 = tmethod.client_ping_dest_not_allowed(self.target_station_2, sta1_wifi_ip_addr)
            if errmsg1 or errmsg2:
                error_at_wlan.append(wlan['ssid'])
                msg = '[Incorrect Behavior] %s, %s while Wireless Client Isolation is enabled on wlan "%s"'
                msg = msg % (errmsg1, errmsg2, wlan['ssid'])
                logging.info(msg)

        return error_at_wlan

    def _checkStationAssociation(self, station, wlan_conf):
        station.remove_all_wlan()
        errmsg = tmethod.assoc_station_with_ssid(station, wlan_conf, self.check_status_timeout)
        if errmsg:
            raise Exception(errmsg)
        val, val1, val2 = tmethod.renew_wifi_ip_address(station, self.check_status_timeout)
        if not val:
            raise Exception(val2)
        else:
            sta_wifi_ip_addr = val1
        return sta_wifi_ip_addr

