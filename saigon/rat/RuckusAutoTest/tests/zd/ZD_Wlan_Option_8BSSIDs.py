# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_Wlan_Option_8BSSIDs is uesed to verify if we could create BSSIDs and station could access
             to both of BSSIDs successfully.

Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters: 'number_bssid': Number of BSSIDs will be tested
                    'target_station': IP address of the station on that we will do the association
                    'active_ap': AP symbolic name or MAC address of the AP that we want to test

   Result type: PASS/FAIL
   Results:
   FAIL:
   - If can not create apropriate number of BSSIDs, or,
   - If we could not access to any of BSSIDs that we create.
   PASS:
   - We can create and access to both of BSSIDs.

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
         1. Config:
            - Delete all wlan on the ZD
         2. Test procedure:
            - Create apropriate number of BSSIDs on the ZD
            - Check if BSSIDs is actived on the AP side or not
            - Check if we could access to BSSIDs or not
         3. Cleanup:
            - Delete all wlan on ZD and station
    How it was tested:
"""

import os
import re
import time
import logging
import random

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from test.test_iterlen import len

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_Wlan_Option_8BSSIDs(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_station': 'ip address of target station',
                           'active_ap': 'mac address (NN:NN:NN:NN:NN:NN) of target ap which client will associate to',
                           'number_bssid': 'Number of BSSIDs will be tested'}

    def config(self, conf):
        # Define test parameters
        self._initTestParams(conf)
        # Get the test AP list
        self._getTestAPList()
        # Repair the target station for the testing
        self._cfgTargetStation()
        # Repair the Zone Director for the testing
        self._cfgZoneDirector()

    def test(self):
        logging.info('Create %d BSSIDs on the ZD' % self.number_bssid)
        configurate_wlans = [self.testbed.components['ZoneDirector'].cfg_wlan(wlan_cfg)
                             for wlan_cfg in self.wlan_config_list]
        wlan_list_on_zd = self.testbed.components['ZoneDirector'].get_wlan_list()
        logging.info('Get Wlan name list on the ZD: %s' % repr(wlan_list_on_zd))
        if len(wlan_list_on_zd) < self.number_bssid:
            msg = 'There are %d wlans be created on ZD instead of %d' % (len(wlan_list_on_zd), self.number_bssid)
            return ('FAIL', msg)

        # Verify if there are wlans be created on APs or not.
        for ap in self.ap_list:
            number_wlans = len(ap.get_wlan_info_dict())

            if number_wlans < len(wlan_list_on_zd):
                msg = 'Number wlan on AP (%s, %s) is not same with the Zone Director'
                msg = msg % (ap.get_ap_model(), ap.ip_addr)
                return 'FAIL', msg

            else:
                msg = 'There are %d wlan on the AP (%s, %s)' % (number_wlans, ap.get_ap_model(), ap.ip_addr)
                logging.info(msg)


        # Verify if from client we could access to BSSIDs or not.
        if self.flag:
            # Turn off the non active APs in our system
            self._cfgActiveAPs()

        connect_summary = []
        for wlan_cfg in self.wlan_config_list:
            basetime = time.time()
            timeout = 0
            self.target_station.cfg_wlan(wlan_cfg)
            status = self.target_station.get_current_status()
            while status != 'connected' and timeout < self.timeout:
                timeout = time.time() - basetime
                time.sleep(5)
                status = self.target_station.get_current_status()

            logging.info('Try to access to \'%s\': %s' % (wlan_cfg['ssid'], status))
            connect_summary.append([wlan_cfg['ssid'], status])

        list_of_disconnected = []
        for connect_info in connect_summary:
            if connect_info[1] != 'connected':
                list_of_disconnected.append(connect_info)

        if len(list_of_disconnected) > 0:
            return 'FAIL', 'There are %d wlan %s that client could not connect successful with' % \
                   (len(list_of_disconnected), repr(list_of_disconnected))

        else:
            return 'PASS', ''

    def cleanup(self):
        logging.info('Clean up environment')
        self.testbed.components['ZoneDirector'].remove_all_wlan()
        if self.target_station:
            self.target_station.remove_all_wlan()

    def _initTestParams(self, conf):
        # Define test parameters
        self.conf = conf
        self.target_station = None
        self.number_bssid = conf['number_bssid']
        if conf.has_key('timeout'):
            self.timeout = conf['timeout']
        else:
            self.timeout = 180

        # Prepair wlan options for testting
        if conf['test_option'] == 'wep_encrypt':
            self._generateWEPWlanConfig()
        else:
            self._generateWlanConfig()

    def _cfgTargetStation(self):
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.timeout
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _getTestAPList(self):
        # Get the expected Active AP
        self.flag = False
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if self.active_ap:
                self.flag = True
                self.ap_list = [self.active_ap]
                self.active_ap.enable_all_wlan()
            else:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])
        else:
            self.ap_list = self.testbed.components['AP']

    def _cfgActiveAPs(self):
        # Get the Actice APs and disable all wlan interface (non mesh interface) in non active aps
        for ap in self.testbed.components['AP']:
            if ap is not self.active_ap:
                logging.info("Turn off all WLAN interface on non-active AP %s" % ap.get_base_mac())
                ap.remove_all_wlan()

        for wlan_cfg in self.wlan_config_list:
            logging.info("Verify WLAN status on the active AP %s" % self.active_ap.get_base_mac())
            wlan_if = self.active_ap.ssid_to_wlan_if(wlan_cfg['ssid'])
            if not self.active_ap.verify_wlan(wlan_if = wlan_if):
                return ("FAIL", "WLAN %s on active AP %s is not up" % (wlan_if,
                        self.active_ap.get_base_mac()))
        

    def _cfgZoneDirector(self):
        logging.info("Remove all wlan configuration on the Zone Director")
        self.testbed.components['ZoneDirector'].remove_all_wlan()

    def _generateWEPWlanConfig(self):
        # Open-WEP-64
        self.wlan_config_list = []
        wlan_cfg = dict(auth = "open", encryption = "WEP-64",
                        key_index = "1" , key_string = utils.make_random_string(10, "hex"))
        for index in range(self.conf['number_bssid']):
            wlan_cfg['ssid'] = self._defineWlanName(index + 1, wlan_cfg)
            self.wlan_config_list.append(utils.generate_wlan_parameter(wlan_cfg))


    def _generateWlanConfig(self):
        self.wlan_config_list = []
        # Open
        wlan_1 = dict(auth = "open", encryption = "none")

        # Open-WEP-128
        wlan_2 = dict(auth = "open", encryption = "WEP-128",
                      key_index = "1" , key_string = utils.make_random_string(26, "hex"))

        # Shared-WEP-64
        wlan_3 = dict(auth = "shared", encryption = "WEP-64",
                      key_index = "1" , key_string = utils.make_random_string(10, "hex"))

        # Shared-WEP-128
        wlan_4 = dict(auth = "shared", encryption = "WEP-128",
                      key_index = "3" , key_string = utils.make_random_string(26, "hex"))

        # WPA-PSK-TKIP
        wlan_5 = dict(auth = "PSK", wpa_ver = "WPA", encryption = "TKIP",
                      sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "TKIP",
                      key_string = utils.make_random_string(random.randint(8, 63), "hex"))

        # WPA-PSK-AES
        wlan_6 = dict(auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                      sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
                      key_string = utils.make_random_string(random.randint(8, 63), "hex"))

        # WPA2-PSK-TKIP
        wlan_7 = dict(auth = "PSK", wpa_ver = "WPA2", encryption = "TKIP",
                      sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "TKIP",
                      key_string = utils.make_random_string(random.randint(8, 63), "hex"))

        # WPA2-PSK-AES
        wlan_8 = dict(auth = "PSK", wpa_ver = "WPA2", encryption = "AES",
                      sta_auth = "PSK", sta_wpa_ver = "WPA2", sta_encryption = "AES",
                      key_string = utils.make_random_string(random.randint(8, 63), "hex"))

        wlan_list = [wlan_1, wlan_2, wlan_3, wlan_4, wlan_5, wlan_6, wlan_7, wlan_8]
        if len(wlan_list) < self.number_bssid:
            for i in range(self.number_bssid - len(wlan_list)):
                wlan_list.append(wlan_1)

        index = 0
        for wlan_cfg in wlan_list:
            index += 1
            wlan_cfg['ssid'] = self._defineWlanName(index, wlan_cfg)
            self.wlan_config_list.append(utils.generate_wlan_parameter(wlan_cfg))

    def _defineWlanName(self, index, wlan_cfg):
        wlan_name = 'wlan %d - %s'
        info = ''
        if wlan_cfg.has_key('wpa_ver'):
            info = '%s_%s_%s' % (wlan_cfg['wpa_ver'], wlan_cfg['auth'], wlan_cfg['encryption'])
        else:
            info = '%s_%s' % (wlan_cfg['auth'].upper(), wlan_cfg['encryption'])
        return wlan_name % (index, info)
