# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script is use to verify the test case 32 WLANs integration with the 'Block client' option.
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'target_station': IP address of the target station.
                    'wlan_config_set': List of 32 WLAN configurations will be test.
                                       Default 32 WLANs with 'Open - None'encryption will be test.

   Result type: PASS/FAIL/ERROR
   Results: FAIL: If any verifying case is fail.
            PASS: We could block the target station and it could not access to any WLAN of 32 WLANs.

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
        - Create 32 WLANs on the Zone Director base on the 'wlan_config_set' parameter
   2. Test:
        - Assign 32 WLANs to Default group continuously to verify:
            + Verify target station access to all WLANs successfully.
        - Block the target station.
        - Verify target station could not access to any WLAN.
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

class ZD_MultiWlans_Block_Client_Integration(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    test_parameters = {'target_station': 'IP address of the target station.',
                        'wlan_config_set': 'List of 32 WLAN configurations will be test.\
                                            Default 32 WLANs with "Open - None"encryption will be test.'}

    def config(self, conf):
        self._initTestParameter(conf)
        self._cfgZoneDirector()
        self._cfgTargetStation()

    def test(self):
        # Block target station
        self._blockTargetStation()
        # Blocked station could not access to any wlans
        self._verifyBlokedStationCouldNotAccessAnyWlan()

        if self.errmsg: return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info("Remove all configuration on the Zone Director")
        # Unblock all blocked clients
        self.zd.unblock_clients('')
        # Delete all wlans on Zone Director
        lib.zd.wlan.delete_all_wlans(self.zd)
        # Remove all wlan profiles on target station
        if self.target_station:
            self.target_station.remove_all_wlan()

    def _initTestParameter(self, conf):
        self.conf = {'target_station':'',
                     'wlan_config_set':'set_of_32_open_none_wlans',
                     'tested_wlan_list': []}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.target_station = None
        self.wlan_conf_list = tconfig.get_wlan_profile(self.conf['wlan_config_set'])
        self.wlan_name_list = [wlan['ssid'] for wlan in self.wlan_conf_list]
        self.check_status_timeout = 180
        self.negative_check_status_timeout = 20
        self.break_time = 2
        self.test_wlan_number = 6
        self.errmsg = ''
        self.passmsg = ''

    def _cfgTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                       , self.testbed.components['Station']
                                                       , check_status_timeout = self.check_status_timeout
                                                       , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        # Delete all wlans on Zone Director
        lib.zd.wlan.delete_all_wlans(self.zd)
        # Unblock all blocked clients
        self.zd.unblock_clients('')
        # Create wlans set for testing
#        lib.zd.wlan.create_multi_wlans(self.zd, self.wlan_conf_list)
        lib.zdcli.set_wlan.create_multi_wlans(self.zdcli, self.wlan_conf_list)
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')
    
    def _blockTargetStation(self):
        # Connect the station to any wlan then block it
        self.sta_wifi_mac_addr = None
        tmethod.assoc_station_with_ssid(self.target_station, self.wlan_conf_list[0],
                                     self.check_status_timeout, self.break_time)
        val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout, self.break_time)
        if not val:
            raise Exception(val2)
        else:
            self.sta_wifi_mac_addr = val2.lower()

        logging.info('Block the client %s' % self.sta_wifi_mac_addr)
        self.zd.block_clients(self.sta_wifi_mac_addr)

        # Verify if the client mac is recorded in the Blocked Clients table
        blocked_clients = lib.zd.cac.get_blocked_clients_list(self.zd)
        if self.sta_wifi_mac_addr not in blocked_clients:
            raise Exception('Client [%s] does not exist in Blocked Clients table' % self.sta_wifi_mac_addr)

    def _verifyBlokedStationCouldNotAccessAnyWlan(self):
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

        # Verify the block client option on the selected wlans
        val = self._verifyBlokedStationAssociation(verify_wlan_conf_list)
        error_at_wlan.extend(val)

        if error_at_wlan:
            self.errmsg = 'Client [%s] is blocked but still could access to wlans %s'
            self.errmsg = self.errmsg % (self.sta_wifi_mac_addr, str(error_at_wlan))
            return

        self.passmsg = 'Block client option work well on %d wlans' % len(self.wlan_conf_list)

    def _verifyBlokedStationAssociation(self, wlan_conf_list):
        # Verify if the blocked client could access to the wlans
        error_at_wlan = []
        for wlan in wlan_conf_list:
            self.target_station.remove_all_wlan()
            logging.info('Verify on wlan %s' % wlan['ssid'])
            msg = tmethod.assoc_station_with_ssid(self.target_station, wlan, self.negative_check_status_timeout)
            if msg:
                logging.info('[Correct Behavior] - %s' % msg)
            else:
                error_at_wlan.append(wlan['ssid'])
                msg = '[Incorrect Behavior] - Blocked client [%s] still could access to wlan [%s]'
                msg = msg % (self.sta_wifi_mac_addr, str(wlan))
                logging.info(msg)
     
        return error_at_wlan

