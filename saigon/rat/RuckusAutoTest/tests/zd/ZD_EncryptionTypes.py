# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_EncryptionTypes Test class verifies that clients are able to associate to an AP under ZD's control
             for specific encryption. The ability to associate is confirmed via a ping test and clients association
             information from ZD.

Product Line: ZoneFlex

Test_bed_type
    ZoneDirector Test Bed

References

Test_ID/Customer_bug_ID
-    ZD_ENCRYPT_0001-ZD_ENCRYPT_0013

Pre-requisite
-    Client 11g
-    ZF7942, ZF2925

Configuration and Parameters

1.    Please refer to Figure 1, Automation Functional Test Setup.
2.    Configure 1 Wlan on ZD with the following encryption types

1.    Open System
2.    Open-WEP-64 (default key index = 1)
3.    Open-WEP-128 (default key index = 1)
4.    Shared-WEP-64 (default key index = 1)
5.    Shared-WEP-128 (default key index = 1)
6.    WPA-PSK-TKIP
7.    WPA-PSK-AES
8.    WPA2-PSK-TKIP
9.    WPA2-PSK-AES
10.   WPA-TKIP (use radius sever)
11.   WPA-AES (use radius sever)
12.   WPA2-TKIP (use radius sever)
13.   WPA2-AES (use radius sever)

Test Procedure

1.    Configure the Wireless Client in the diagram with the same SSID and encryption setting as the ZoneDirector.
2.    Verify on the ZoneDirector if the Wireless Client is associated by going to the WebUI (https://192.168.0.2) and
      navigating to the Monitor->Currently Active Clients page.
      - Verify other information: MAC Address, channel, radio (802.11bg or 802.11ng), and status (Authorized) are correct.
3.    Verify on the AP if the Wireless Station is associated by SSHing into that AP and checking The Wireless Station
      association status using the 'get station wlan0 list' command.
      - Client MAC Address must be the same as wifi MAC Address on wireless station
      - 'AID' must not be zero.
      - Channel must be the same as shown on ZD
4.    Ping from Wireless station to an uplink server. Verify the ping is successful

Observable Results

- The Wireless Station is able to join the ZoneDirector/AP and pass traffic.
- Wireless clients should perform authentication and association to the ZoneDirector through the AP, and upon successful
  association, be able to pass traffic through the AP without tunneling back to the ZoneDirector.
- Zone Director should display correct information of wireless clients associated

Pass/Fail Criteria (including pass/fail messages)
- The test case passes if all of the verification steps in the test case are met.

How it was tested:
- Using client 11g to run test cases 11n. It should return failed cases because on ZD it will display 802.11b/g while
test code expect 802.11ng. However, encryption (TKIP, WEP-64, WEP-128) will return PASS because 11n run as g mode for
these encryptions.
- Disable wireless card on station so test code could not determine station associated to AP and verify current
active clients on Zone Director.

"""

import os
import re
import time
import logging
from copy import deepcopy

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
#from RuckusAutoTest.components import Station
#from RuckusAutoTest.components import RuckusAP

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_EncryptionTypes(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'ip':'IP address to ping',
                           'target_station':'ip address of target station',
                           'active_ap':'mac address (NN:NN:NN:NN:NN:NN)of target ap which client will associate to',
                           'wlan_cfg':'dictionary of association parameters',
                           'radio_mode':'wireless mode on client  This value must be g or n'}

    def config(self, conf):
        # Testing parameters
        self._cfgInitTestParams(conf)

        # Find the target station object
        self._cfgGetTargetStation()

        self._cfgRemoveZDWlan()

        # Find the active AP object if the parameter 'active_ap' is passed.
        self._cfgGetActiveAP()

    def test(self):
        # Define the authentication server or local user account on the ZD
        self._cfgCreateAuthenticationMethod()

        # Configure a WLAN on the ZD
        self._cfgCreateWlanOnZoneDirector()

        # Remove WLAN on non-active APs and verify WLANs on the active AP
        self._testVerifyWlanOnAPs()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Configure a WLAN on the station and verify the connection status
        self._testStationAssocWithSSID()

        if not self.errmsg:
            # The station has connected to the WLAN successfully
            self._cfgGetStaWifiIpAddress()

            # Verify connectivity from the station to a destination uplink
            self._testStationConnectivity()
            if self.errmsg: return ("FAIL", self.errmsg)
        else:
            # Verify to see if the station could see the SSID broadcasted in the air
            self._testWlanInTheAir()
            if self.errmsg: return ("FAIL", self.errmsg)

        # Verify information of the target station shown on the ZD
        self._testVerifyStationInfoOnZD()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Verify information of the target station shown on the AP
        self._testVerifyStationInfoOnAP()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Everything is ok
        return ("PASS", "")

    def cleanup(self):
        # Remove all configuration from the ZD
        self._cfgRemoveZDWlan()

        # Remove the WLAN from the station
        self._cfgRemoveWlanFromStation()

    def _cfgInitTestParams(self, conf):
        if conf.has_key('wlan_cfg'):
            self.wlan_cfg = conf['wlan_cfg']
        else:
            # Get the default wlan configuration if the parameter 'wlan_cfg' is not passed.
            self.wlan_cfg = {'username': 'local.user', 'sta_auth': 'open', 'ras_port': '',
                             'key_index': '', 'auth': 'open', 'sta_encryption': 'none',
                             'ras_addr': '', 'password': 'local.user', 'ad_domain': '',
                             'ad_port': '', 'ssid': 'vlan_web_auth', 'key_string': '',
                             'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '',
                             'wpa_ver': '', 'ras_secret': '', 'vlan_id': conf['vlan_id']}
        self.conf = conf
        self.wlan_cfg = conf['wlan_cfg']
        self.ping_timeout_ms = 150 * 1000
        self.check_status_timeout = 120
        self.target_ip = conf['ip']
        self.radio_mode = conf['radio_mode']

    def _cfgGetTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.check_status_timeout
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgRemoveZDWlan(self):
        logging.info("Remove all WLAN on the Zone Director")
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)
        #self.testbed.components['ZoneDirector'].remove_all_cfg()

    def _cfgGetActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])

    def _cfgRemoveWlanFromStation(self):
        if self.target_station:
            tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout = self.check_status_timeout)

    def _cfgCreateAuthenticationMethod(self):
        if self.wlan_cfg['auth'] == "EAP":
            logging.info("Create an authentication server on the ZoneDirector")
            if self.wlan_cfg['use_radius']:
                self.testbed.components['ZoneDirector'].create_radius_server(self.wlan_cfg['ras_addr'],
                                                                         self.wlan_cfg['ras_port'], self.wlan_cfg['ras_secret'])
            else:
                logging.info("Create a user on the ZoneDirector")
                self.testbed.components['ZoneDirector'].create_user(self.wlan_cfg['username'], self.wlan_cfg['password'])

    def _cfgCreateWlanOnZoneDirector(self):
        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        if self.wlan_cfg['wpa_ver'] == "WPA_Mixed": 
            lib.zd.wlan.create_wlan(self.testbed.components['ZoneDirector'], self.wlan_cfg)
        else: 
            self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan_cfg)
        #JLIN@20090716 add delay time for ZD8.1 deploy setting to AP 
        time.sleep(10)

    def _testVerifyWlanOnAPs(self):
        self.errmsg = tmethod.verify_wlan_on_aps(self.active_ap, self.wlan_cfg['ssid'], self.testbed.components['AP'])

    def _testStationAssocWithSSID(self):
        wlan_cfg = deepcopy(self.wlan_cfg)
        if self.wlan_cfg['wpa_ver'] == "WPA_Mixed":
            wlan_cfg['wpa_ver'] = wlan_cfg['sta_wpa_ver']
            wlan_cfg['encryption'] = wlan_cfg['sta_encryption']
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station, wlan_cfg, self.check_status_timeout)

    def _cfgGetStaWifiIpAddress(self):
        # Renew the IP address of the wireless adapter on the wireless station
        res, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)

        if not res:
            raise Exception(val2)

        self.sta_wifi_ip_addr = val1
        self.sta_wifi_mac_addr = val2.lower()

    def _testStationConnectivity(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.target_ip, ping_timeout_ms = self.ping_timeout_ms)

    def _testWlanInTheAir(self):
        self.errmsg = tmethod.verify_wlan_in_the_air(self.target_station, self.wlan_cfg['ssid'])

    def _testVerifyStationInfoOnZD(self):
        logging.info("Verify information of the target station shown on the Zone Director")
        if self.radio_mode == 'g' or self.wlan_cfg['encryption'] in ['TKIP', 'WEP-64', 'WEP-128']:
            # 11n does not suport TKIP,WEP-64, WEP-128 encryption
            expected_radio_mode = ['802.11b/g', '802.11a']
        else:
            expected_radio_mode = ['802.11ng', '802.11g/n', '802.11a/n', '802.11an']
        if self.wlan_cfg['auth'] == 'EAP':
            expected_ip = self.wlan_cfg['username']
        else:
            expected_ip = self.sta_wifi_ip_addr
        exp_client_info = {"ip": expected_ip, "status": "Authorized", "wlan": self.wlan_cfg['ssid'],
                           "radio": expected_radio_mode, "apmac": self.active_ap.base_mac_addr}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.testbed.components["ZoneDirector"],
                                                                   self.sta_wifi_mac_addr, exp_client_info,
                                                                   self.check_status_timeout)

    def _testVerifyStationInfoOnAP(self):
        self.errmsg = tmethod.verify_station_info_on_ap(self.active_ap, self.sta_wifi_mac_addr, self.wlan_cfg['ssid'],
                                            self.client_info_on_zd['channel'])

