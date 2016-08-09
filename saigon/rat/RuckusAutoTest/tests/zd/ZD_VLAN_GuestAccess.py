# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
"""
Description: ZD_VLAN_GuestAccess Test class tests the ability of the Zone Director to deploy Guest WLAN with VLAN tagging
             to wireless station

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'ZoneDirector', 'RuckusAP'
   Test parameters: 'ip': 'IP address to ping. Must be given in format n.n.n.n/m.m.m.m',
                    'vlan_id': 'A VLAN ID to assign to the WLAN',
                    'target_station': 'IP address of target station'
                    'active_ap': 'mac address of active ap'

   Result type: PASS/FAIL/ERROR
   Results: PASS: target station can associate, get ip address that is in the same subnet assigned to the VLAN,
                   perform guest authentication, ping to a destination successfully and
                   information is shown correctly in ZD and AP
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration on the Zone Director
       - Remove all guest passes on the ZD
       - Record guest access policy on the ZD
    2. Test:
       - Configure Guest Access policy and configure a user which will be used to generate guest pass
       - Generate a guest pass
       - Configure a Guest WLAN on the ZD with vlan tagging enabled
       - If active ap is used, telnet to non-active aps, remove all wlan on these aps
       - Configure the target station with given security setting
       - Get IP and MAC address of the wireless adapter on the wireless client
       - Verify if the IP address is in the same subnet with the given IP address (address to ping)
       - Verify the station status shown on the ZD is "Unauthorzied"
       - Do a guest authentication
       - Do a ping again to make sure traffic gets forwarded to the given IP address
       - Verify if the ZD shows correct information about the connected station one more time
   3. Cleanup:
       - Return the original configuration of guest access policy on the ZD
       - Remove all wlan configuration and generated guest passes on ZD
       - Remove wireless profile on remote wireless STA
       - Verify if wireless station is completely disconnected after removing the wireless profile

   How it is tested?
       - After the client has associated to the WLAN and do a guest authentication successfully,
        log on the wireless client and disconnect the connection.
        The script must report that the ping to destination could not be done.
"""

import os
import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

class ZD_VLAN_GuestAccess(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'ip': 'IP address to ping. Must be given in format n.n.n.n/m.m.m.m',
                           'target_station': 'ip address of target station',
                           'active_ap': 'MAC address of active ap',
                           'vlan_id': 'a valid VLAN ID'}

    def config(self, conf):
        # Define test parameters
        self._cfgInitTestParams(conf)

        # Find the target station object and remove all WLAN profiles
        self._cfgTargetSation()

        # Remove all configuration on the ZD and configure the WLAN, guest access policy
        self._cfgZoneDirector()

        # Generate a guest pass
        self._cfgGenerateGuestPass()

        # Determine DUT AP (active_ap)
        # and turn-off wlan on non-active AP to ensure wireless client only associate to DUT AP
        self._cfgActiveAP()

    def test(self):
        # Configure the wireless station to join the WLAN
        self._cfgWlanOnStation(expected_status = "connected")

        # Verify the IP address obtained on the wireless station
        self._testStaWifiIpAddress()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Make sure the client is not permited to transmit traffic
        self._testStationPingBeforeAuthen()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Verify the status of the client shown on ZD
        self._testVerifyStationInfoOnZDBeforeAuthen()
        if self.errmsg: return ("FAIL", self.errmsg)

        logging.info("Perform Guest Pass authentication on the target station %s" % self.target_station.get_ip_addr())

        arg = tconfig.get_guest_auth_params(self.zd, self.guest_pass, self.use_tou, self.redirect_url)
        self.target_station.perform_guest_auth(arg)

        # Make sure the client is permited to transmit traffic
        self._testStationPingAfterAuthen()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Verify the status of the client shown on ZD
        self._testVerifyStationInfoOnZDAfterAuthen()
        if self.errmsg: return ("FAIL", self.errmsg)

        return ("PASS", "")

    def cleanup(self):
        #logging.info("Remove all the WLANs on the Zone Director")
        #self.zd.remove_all_cfg()

        #logging.info("Remove all Guest Passes created on the Zone Director")
        #self.zd.remove_all_guestpasses()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        if self.current_guest_access_policy:
            logging.info("Restore Guest Access Policy to original configuration on ZD")
            self.zd.set_guestaccess_policy(**self.current_guest_access_policy)

        if self.target_station:
            logging.info("Remove all WLAN profiles on the remote station")
            self.target_station.remove_all_wlan()

            logging.info("Make sure the target station disconnects from the wireless networks")
            start_time = time.time()
            while True:
                if self.target_station.get_current_status() == "disconnected":
                    break
                time.sleep(1)
                if time.time() - start_time > self.check_status_timeout:
                    raise Exception("The station did not disconnect from wireless network within %d seconds" %
                                    self.check_status_timeout)

    def _cfgInitTestParams(self, conf):
        self.conf = conf
        self.current_guest_access_policy = None
        self.use_tou = False
        self.username = "guest_netanya_test"
        self.password = "123456789"
        self.guest_name = "Guest Netanya"
        self.redirect_url = ""
        self.check_status_timeout = 150
        self.ping_timeout = 150
        self.target_station = None
        self.active_ap = None
        self.vlan_id = conf['vlan_id']
        self.zd = self.testbed.components['ZoneDirector']

        ip_list = conf['ip'].split("/")
        self.ip_addr = ip_list[0]
        if len(ip_list) == 2:
            self.mask = ip_list[1]
        else:
            self.mask = ""

        self.wlan_cfg = {'ssid': 'rat-vlan-guest-access', 'auth': 'PSK', 'wpa_ver': 'WPA2', 'encryption': 'AES',
                         'sta_auth': 'PSK', 'sta_wpa_ver': 'WPA2', 'sta_encryption': 'AES',
                         'key_string': utils.make_random_string(63, "hex"), 'key_index': '', 'vlan_id': self.vlan_id,
                         'username': '', 'password': '', 'ras_addr': '', 'ras_port': '', 'ras_secret': '',
                         'ad_addr': '', 'ad_port': '', 'ad_domain': '', 'use_guest_access': True}

    def _cfgTargetSation(self):
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(self.conf['target_station'],
                                               self.testbed.components['Station'],
                                               check_status_timeout = self.check_status_timeout,
                                               remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgZoneDirector(self):
        #logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()

        #logging.info("Remove all Guest Passes created on the Zone Director")
        #self.zd.remove_all_guestpasses()

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        logging.info("Record current Guest Access Policy on the ZD")
        self.current_guest_access_policy = self.zd.get_guestaccess_policy()

        logging.info("Configure Guest Access policy on the Zone Director")
        self.zd.set_guestaccess_policy(use_guestpass_auth = True, use_tou = self.use_tou, redirect_url = self.redirect_url)

        logging.info("Create a user on the Zone Director")
        self.zd.create_user(self.username, self.password)

        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        self.zd.cfg_wlan(self.wlan_cfg)

    def _cfgGenerateGuestPass(self):
        logging.info("Generate a Guest Pass on the ZD")
        self.guest_pass, expired_time = self.zd.generate_guestpass(self.username, self.password, self.guest_name, "1", "Days")

    def _cfgActiveAP(self):
        # Find the Active AP and disable all non-mesh WLAN interfaces on the other APs
        # Get the Actice AP and disable all wlan interface (non mesh interface) in non active aps
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if self.active_ap:
                self.errmsg = tmethod.verify_wlan_on_aps(self.active_ap, self.wlan_cfg['ssid'], self.testbed.components['AP'])
            else:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])

    def _cfgWlanOnStation(self, expected_status):
        logging.info("Configure a WLAN with SSID %s on the target station %s" % (self.wlan_cfg['ssid'],
                                                                                 self.target_station.get_ip_addr()))
        self.target_station.cfg_wlan(self.wlan_cfg)

        logging.info("Make sure the station associates to the WLAN")
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == expected_status:
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                msg = "The station did not associate to the wireless network within %d seconds" % \
                      self.check_status_timeout
                raise Exception(msg)

    def _testStaWifiIpAddress(self):
        # Renew the IP address of the wireless adapter on the wireless station
        res, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)

        if not res:
            raise Exception(val2)

        self.sta_wifi_ip_addr = val1
        self.sta_wifi_mac_addr = val2.lower()

        self.errmsg = ""
        logging.info("Make sure that the client has got an IP address assigned to the VLAN")
        if utils.get_network_address(self.sta_wifi_ip_addr, self.mask) != utils.get_network_address(self.ip_addr, self.mask):
            msg = "The IP address %s was not in the same subnet as %s." % (self.sta_wifi_ip_addr, self.ip_addr)
            msg += " Traffic sent from the wireless station was not tagged properly"
            self.errmsg = msg

    def _testStationPingBeforeAuthen(self):
        # In guest access authentication, when client is unauthorized, the ZD shows IP address of the client
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.ip_addr, ping_timeout_ms = 5000)

    def _testVerifyStationInfoOnZDBeforeAuthen(self):
        (self.errmsg, self.client_info_on_zd) = tmethod.verify_zd_client_is_unauthorized(self.zd,
                                                                             self.sta_wifi_ip_addr, self.sta_wifi_mac_addr,
                                                                             self.check_status_timeout)

    def _testStationPingAfterAuthen(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.ip_addr, ping_timeout_ms = self.ping_timeout * 1000)

    def _testVerifyStationInfoOnZDAfterAuthen(self):
        # In guest access authentication, after the client is authorized, the ZD shows username used to authenticate of the client
        (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_authorized(self.zd,
                                                                     self.guest_name, self.sta_wifi_mac_addr,
                                                                     self.check_status_timeout)

