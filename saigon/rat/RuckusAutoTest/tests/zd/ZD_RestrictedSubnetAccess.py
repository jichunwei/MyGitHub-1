# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_RestrictedSubnetAccess Test class tests the ability of a station to associate with an AP under ZD's control
with open security configuration and Guest Pass authentication mechanism. The ability to associate is confirmed
via a ping test.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'restricted_ip_list': 'List of IP addresses that are restricted from guest clients',
                    'zd_ip': 'IP address of Zone Director',
                    'allowed_ip': 'An IP address that is not restricted',
                    'target_station': 'IP address of target station',

   Result type: PASS/FAIL/ERROR
   Results: PASS: target station can associate, do Guest authentication, can ping to a destination that is not
                  in the restricted list, and can't ping to any destinations that are in the restricted list
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
       - Remove all guest passes if existed
   2. Test:
       - Configure a WLAN on the ZD with open security setting
       - Configure Guest Access policy and configure a user which will be used to generate guest pass
       - Go to page Restricted Subnet Access and enter the subnets that are specified to the list
       - Open another browser, browse to the Guest Pass Generation page and generate a guest pass
       - Configure the target station with given security setting
       - Wait until it gets associated and get IP and MAC addresses of the wireless adapter
       - Do Guest authentication with the generated guest pass from the station
       - Ping to the IP that is not in the restricted list, the ping should be done ok
       - Ping to the addresses that are in the restricted list and make sure that they can not be done
       - Ping to the ZD and this should not be done successfully either
   3. Cleanup:
       - Remove all wlan configuration and generated guest passes on ZD
       - Remove wireless profile on remote wireless STA
       - Verify that wireless station is completely disconnected after removing the wireless profile.

   How it is tested?
       - After the client has done the authentication successfully, go to the table Active Clients and delete that
         user. The script should report that the client cannot ping to the address that should be pingable
"""

import os
import re
import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_RestrictedSubnetAccess(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'restricted_ip_list': 'List of IP addresses that are restricted from guest clients',
                           'zd_ip': 'IP address of Zone Director',
                           'allowed_ip': 'An IP address that are not restricted',
                           'target_station': 'IP address of target station'}

    def config(self, conf):
        # Define test parameters
        self._initTestParams(conf)
        # Repair the target station for the testing
        self._cfgTargetSation()
        # Repair the Zone Director for the testing
        self._cfgZoneDirector()

    def test(self):
        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        self.zd.cfg_wlan(self.wlan_cfg)

        logging.info("Configure Guest Access policy on the Zone Director")
        self.zd.set_guestaccess_policy(use_guestpass_auth = self.use_guest_auth,
                                       use_tou = self.use_tou,
                                       redirect_url = self.redirect_url)
        logging.debug("New Guest Access Policy use_guestpass_auth=%s --- use_tou=%s --- redirect_url=%s" %
                      (self.use_guest_auth, self.use_tou, self.redirect_url))

        logging.info("Configure Restricted Subnet Access on the Zone Director")
        self.zd.set_restricted_subnets(self.restricted_subnet_list)

        logging.info("Create a user on the Zone Director")
        self.zd.create_user(self.username, self.password)

        logging.info("Generate a Guest Pass on the ZD")
        guest_pass, expired_time = self.zd.generate_guestpass(self.username, self.password,
                                                              self.guest_name, "1", "Days")

        # Turn off all wlan interface on non active APs.
        self._cfgActiveAPs()

        logging.info("Configure a WLAN with SSID %s on the target station %s" % (self.wlan_cfg['ssid'],
                                                                                 self.target_station.get_ip_addr()))
        self.target_station.cfg_wlan(self.wlan_cfg)

        logging.info("Make sure the station associates to the WLAN")
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "connected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                raise Exception("The station didn't associate to the wireless network after %d seconds" % \
                                self.check_status_timeout)

        logging.info("Renew IP address of the wireless adapter on the target station")
        self.target_station.renew_wifi_ip_address()

        logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" %
                     self.target_station.get_ip_addr())
        start_time = time.time()
        sta_wifi_ip_addr = None
        sta_wifi_mac_addr = None
        while time.time() - start_time < self.check_status_timeout:
            sta_wifi_ip_addr, sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
            if sta_wifi_mac_addr and sta_wifi_ip_addr and sta_wifi_ip_addr != "0.0.0.0":
                break
            time.sleep(1)
        logging.debug("Wifi IP: %s ---- Wifi MAC: %s" % (sta_wifi_ip_addr, sta_wifi_mac_addr))
        if not sta_wifi_mac_addr:
            msg = "Unable to get MAC address of the wireless adapter of the target station %s" % \
                  self.target_station.get_ip_addr()
            raise Exception(msg)
        if not sta_wifi_ip_addr:
            msg = "Unable to get IP address of the wireless adapter of the target station %s" % \
                  self.target_station.get_ip_addr()
            raise Exception(msg)
        if sta_wifi_ip_addr == "0.0.0.0" or sta_wifi_ip_addr.startswith("169.254"):
            msg = "The target station %s could not get IP address from DHCP server" % \
                  self.target_station.get_ip_addr()
            return ("FAIL", msg)

        time.sleep(5)
        logging.info("Perform Guest Pass authentication on the target station %s" % self.target_station.get_ip_addr())
        arg = tconfig.get_guest_auth_params(self.zd, guest_pass, self.use_tou, self.redirect_url)
        self.target_station.perform_guest_auth(arg)

        logging.info("Ping to %s which is not in the restricted list" % self.allowed_ip)
        ping_result = self.target_station.ping(self.allowed_ip, 5 * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Incorrect behavior")
            return ("FAIL", "The target station could not ping to %s while it was not in the restricted subnet")
        else:
            logging.info("Ping OK. Correct behavior")

        logging.info("Ping to %s which is in the subnet of Zone Director" % self.zd_ip)
        ping_result = self.target_station.ping(self.zd_ip, 5 * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Correct behavior")
        else:
            logging.info("Ping OK. Incorrect behavior")
            return ("FAIL", "The target station could ping to %s while it was in the subnet of Zone Director" % self.zd_ip)

        logging.info("Ping to destinations in the restricted list from the target station %s" %
                     self.target_station.get_ip_addr())
        for ip in self.restricted_ip_list:
            logging.info("Ping to %s" % ip)
            ping_result = self.target_station.ping(ip, 5 * 1000)
            if ping_result.find("Timeout") != -1:
                logging.info("Ping FAILED. Correct behavior")
            else:
                logging.info("Ping OK. Incorrect behavior")
                return ("FAIL", "The target station could ping to %s while it was in the restricted subnet" % ip)

        return ("PASS", "")

    def cleanup(self):
        logging.info("Remove all the WLANs on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        #logging.info("Remove all Guest Pass created on the Zone Director")
        #self.zd.remove_all_guestpasses()

        if self.current_guest_access_policy:
            logging.info("Restore Guest Access Policy to original configuration on ZD")
            self.zd.set_guestaccess_policy(**self.current_guest_access_policy)

        if self.current_guest_pass_policy:
            logging.info("Restore Guest Password Policy to original configuration on ZD")
            self.zd.set_guestpass_policy(**self.current_guest_pass_policy)

        if self.current_restricted_list:
            logging.info("Restore original configured restricted subnets on ZD")
            self.zd.set_restricted_subnets(self.current_restricted_list)

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

    def _initTestParams(self, conf):
        # Define test parameters
        # Security setting used for the test is open-none
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                         'sta_encryption': 'none', 'ras_addr': '', 'password': '', 'use_guest_access': True,
                         'ad_domain': '', 'ad_port': '', 'ssid': 'rat-guest-access-testing', 'key_string': '',
                         'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'wpa_ver': '', 'ras_secret': ''}
        self.conf = conf
        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.allowed_ip = conf['allowed_ip']
        self.zd_ip = conf['zd_ip']
        self.restricted_ip_list = conf['restricted_ip_list']
        self.restricted_subnet_list = []
        for ip in self.restricted_ip_list:
            self.restricted_subnet_list.append("%s/%s" % (utils.get_network_address(ip), utils.get_subnet_mask(ip)))
        self.use_guest_auth = True
        self.use_tou = True
        self.redirect_url = ''
        self.username = "ruckus"
        self.password = "ruckus"
        self.guest_name = "Retriever"
        self.current_guest_access_policy = None
        self.current_guest_pass_policy = None
        self.current_restricted_list = None
        self.target_station = None

        self.zd = self.testbed.components['ZoneDirector']

    def _cfgTargetSation(self):
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
        logging.info("Remove all WLAN on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        logging.info("Record current configured restricted subnets on ZD")
        self.current_restricted_list = self.zd.get_restricted_subnets()

        logging.info("Record current Guest Access Policy on ZD")
        self.current_guest_access_policy = self.zd.get_guestaccess_policy()

        logging.info("Record current Guest Password Policy on the ZD")
        self.current_guest_pass_policy = self.zd.get_guestpass_policy()

        logging.info("Remove all Guest Pass created on the Zone Director")
        self.zd.remove_all_guestpasses()

