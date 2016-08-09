# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_Wireless_Client_Isolation Test class verifies if clients can associate to a WLAN created on ZoneDirector
             and can not ping to each other when the feature 'Wireless Client Isolation' is enabled.
             This test is confirmed via a ping test and the addresses acquired on the clients.

Product Line: ZoneDirector

Test_bed_type: ZoneDirector Test Bed

References

Test_ID/Customer_bug_ID:
     - ZD_CLIENT_ISOLATION_0001

Pre-requisite:
     - At least 2 clients supporting 11g
     - ZF2942 and/or ZF2925 and/or ZF7942

Configuration and Parameters:
     {'target_station': 'ip address of target station'}

Test Procedure:
     - Config:
         + Make sure that the testbed has at least 2 clients.
         + Look for the target station and remove all WLAN(s) on that station.
         + Look for another station (destination station) and remove all WLAN(s) on that station.
         + Remove all WLAN(s) on the ZoneDirector.
     - Test:
         + Create a WLAN on the ZoneDirector.
         + Create a WLAN profile on the target station.
         + Make sure that the target station associates successfully.
         + Verify if the target station can get the IP and the MAC addresses.
         + Create a WLAN profile on the destination station.
         + Make sure that the destination station associates successfully.
         + Verify if the destination station can get the IP and the MAC addresses.
         + Ping from the target station to another client, make sure that this ping fails.
     - Cleanup:
         + Remove all WLAN(s) on the ZoneDirector.
         + Remove all WLAN profiles on the target station. Make sure that it completely disconnects from the WLAN.
         + Remove all WLAN profiles on the destination station. Make sure that it completely disconnects from the WLAN.

Observable Result:
     - A WLAN is created.
     - The target and destination stations asscociate and get IP and MAC addresses but can not ping to each other.
     - The target and destination stations disconnect from the WLAN.

Pass/Fail Criteria (including pass/fail messages)
- The test case passes if all of the verification steps in the test case are met.

How it was tested:
     - If there is only one client in the testbed, the script must return ERROR.
     - During the ping, disable the feature 'Wireless Client Isolation', the script must return FAIL.

"""

import os
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_Wireless_Client_Isolation(Test):
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
        self.target_station = None
        self.destination_station = None

        # The testbed has at least 2 stations
        if len(self.testbed.components['Station']) < 2:
            raise Exception("There are fewer than 2 stations in the testbed. There must be at least 2 stations.")

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

        # Find the destination station object and remove all Wlan profiles. The destination station is the station to which
        # the starget station ping to test the feature of Client Isolation.
        for station in self.testbed.components['Station']:
            if station.get_ip_addr() != conf['target_station']:
                # Found the destination station
                self.destination_station = station

                logging.info("Remove all WLAN profiles on the destination station %s" %
                             self.destination_station.get_ip_addr())
                self.destination_station.remove_all_wlan()

                logging.info("Make sure the destination station %s disconnects from wireless network" %
                             self.destination_station.get_ip_addr())
                start_time = time.time()
                while True:
                    if self.destination_station.get_current_status() == "disconnected":
                        break
                    time.sleep(1)
                    if time.time() - start_time > self.check_status_timeout:
                        raise Exception("The station did not disconnect from wireless network within %d seconds" %
                                        self.check_status_timeout)
                break
        if not self.destination_station:
            raise Exception("Destination station is not found")

        logging.info("Remove all configuration on the Zone Director")
        #self.testbed.components['ZoneDirector'].remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

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

        logging.info("Configure a WLAN with SSID %s on the destination station %s" % (self.wlan_cfg['ssid'],
                                                                                 self.destination_station.get_ip_addr()))
        self.destination_station.cfg_wlan(self.wlan_cfg)

        logging.info("Make sure the destination station associates to the WLAN")
        start_time = time.time()
        while True:
            if self.destination_station.get_current_status() == "connected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                msg = "The station did not associate to the wireless network within %d seconds" % \
                      self.check_status_timeout
                raise Exception(msg)

        logging.info("Renew IP address of the wireless adapter on the destination station")
        self.destination_station.renew_wifi_ip_address()

        logging.info("Get IP and MAC addresses of the wireless adapter on the destination station %s" %
                     self.destination_station.get_ip_addr())
        start_time = time.time()
        sta_wifi_ip_addr = None
        sta_wifi_mac_addr = None
        while time.time() - start_time < self.check_status_timeout:
            sta_wifi_ip_addr, sta_wifi_mac_addr = self.destination_station.get_wifi_addresses()
            if sta_wifi_mac_addr and sta_wifi_ip_addr and sta_wifi_ip_addr != "0.0.0.0":
                break
            time.sleep(1)
        logging.debug("Wifi IP: %s ---- Wifi MAC: %s" % (sta_wifi_ip_addr, sta_wifi_mac_addr))
        if not sta_wifi_mac_addr:
            msg = "Unable to get MAC address of the wireless adapter of the target station %s" % \
                  self.destination_station.get_ip_addr()
            raise Exception(msg)
        if not sta_wifi_ip_addr:
            msg = "Unable to get IP address of the wireless adapter of the target station %s" % \
                  self.destination_station.get_ip_addr()
            raise Exception(msg)
        if sta_wifi_ip_addr == "0.0.0.0" or sta_wifi_ip_addr.startswith("169.254"):
            msg = "The target station %s could not get IP address from DHCP server" % \
                  self.destination_station.get_ip_addr()
            return ("FAIL", msg)

        # Ping from the target station to another client, make sure that this ping fails.
        logging.info("Ping to %s from the target station (timeout: %s)" %
                     (self.destination_station.get_ip_addr(), self.ping_timeout))
        ping_result = self.target_station.ping(sta_wifi_ip_addr, self.ping_timeout * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Correct behavior")
        else:
            logging.info("Ping OK. Incorrect behavior")
            return ("FAIL", "The target station could send traffic to the client '%s'." %
                    self.destination_station.get_ip_addr())

        return ("PASS", "")

    def cleanup(self):
        logging.info("Remove all WLAN(s) on the Zone Director")
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

        if self.destination_station:
            logging.info("Remove all WLAN profiles on the destination station")
            self.destination_station.remove_all_wlan()

            logging.info("Make sure the destination station disconnects from the wireless networks")
            start_time = time.time()
            while True:
                if self.destination_station.get_current_status() == "disconnected":
                    break
                time.sleep(1)
                if time.time() - start_time > self.check_status_timeout:
                    raise Exception("The destination station did not disconnect from wireless network within %d seconds" %
                                    self.check_status_timeout)

