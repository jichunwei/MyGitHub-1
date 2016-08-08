# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_Wireless_Client_ZD_Default_Subnet_Isolation Test class verifies if a client can associate to a
             WLAN created on ZoneDirector and can not ping to the ZoneDirector when the feature
             'Wireless Client Isolation' is enabled. The test is confirmed via a ping test and
             the addresses acquired on the client.

Product Line: ZoneDirector

Test_bed_type: ZoneDirector Test Bed

References

Test_ID/Customer_bug_ID:
     - ZD_CLIENT_ISOLATION_0002

Pre-requisite:
     - 1 client supports 11g
     - ZF2942 and/or ZF2925 and/or ZF7942

Configuration and Parameters:
     {'target_station': 'ip address of target station'}

Test Procedure:
     - Config:
         + Look for the target station and remove all WLAN(s) on that station.
         + Remove all WLAN(s) on the ZoneDirector.
     - Test:
         + Create a WLAN on the ZoneDirector.
         + Create a WLAN profile on the target station.
         + Make sure that the target station associates successfully.
         + Verify if the target station can get the IP and the MAC addresses.
         + Ping from the target station to the ZoneDirector, make sure that this ping fails.
     - Cleanup:
         + Remove all WLAN(s) on the ZoneDirector.
         + Remove all WLAN profiles on the target station. Make sure that it completely disconnects from the WLAN.

Observable Result:
     - A WLAN is created.
     - The target station associates and gets IP and MAC addresses but can not ping to each other.
     - The target station disconnects from the WLAN.

Pass/Fail Criteria (including pass/fail messages)
- The test case passes if all of the verification steps in the test case are met.

How it was tested:
     - During the ping, disable the feature 'Wireless Client Isolation', the script must return FAIL.

"""

import os
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_Wireless_Client_ZD_Default_Subnet_Isolation(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_station': 'ip address of target station'}

    def config(self, conf):
        # Testing parameters
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                                     'sta_encryption': 'none', 'ras_addr': '', 'password': '', 'ad_domain': '',
                                     'ad_port': '', 'ssid': 'wlan_client_isolation', 'key_string': '',
                                     'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'wpa_ver': '',
                                     'ras_secret': '', 'use_client_isolation':True}
        self.ping_timeout = 150
        self.check_status_timeout = 120

        # Find the target station object and remove all Wlan profiles
        for station in self.testbed.components['Station']:
            if station.get_ip_addr() == conf['target_station']:
                # Found the target station
                self.target_station = station

                logging.info("Remove all WLAN profiles on the target station %s" % self.target_station.get_ip_addr())
                self.target_station.remove_all_wlan()

                logging.info("Make sure the target station %s disconnects from wireless network" %
                             self.target_station.get_ip_addr())
                start_time = time.time()
                while True:
                    if self.target_station.get_current_status() == "disconnected":
                        break
                    time.sleep(1)
                    if time.time() - start_time > self.check_status_timeout:
                        raise Exception("The station did not disconnect from wireless network within %d seconds" %
                                        self.check_status_timeout)
                break
        if not self.target_station:
            raise Exception("Target station % s not found" % conf['target_station'])

        # Get the IP address of the Zone Director
        self.zd_ip_addr = self.testbed.components['ZoneDirector'].ip_addr

        logging.info("Remove all WLAN(s)on the Zone Director")
        self.testbed.components['ZoneDirector'].remove_all_wlan()

    def test(self):
        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan_cfg)

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
                msg = "The station did not associate to the wireless network within %d seconds" % \
                      self.check_status_timeout
                raise Exception(msg)

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

        # Ping to the ZoneDirector from the target station, make sure that this ping fails.
        logging.info("Ping to the ZoneDirector from the target station (timeout: %s)" % (self.ping_timeout))
        ping_result = self.target_station.ping(self.zd_ip_addr, self.ping_timeout * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Correct behavior")
        else:
            logging.info("Ping OK. Incorrect behavior")
            return ("FAIL", "The target station could ping the ZD while the client isolation is enabled.")

        return ("PASS", "")

    def cleanup(self):
        logging.info("Remove all WLAN(s)on the Zone Director")
        self.testbed.components['ZoneDirector'].remove_all_wlan()

        if self.target_station:
            logging.info("Remove all WLAN profiles on the target station")
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

