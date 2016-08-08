# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_Wireless_Client_Isolation_For_Specific_AP Test class verifies if clients:
                 - can associate to a WLAN on an active AP(2925, 2942 or 7942)
                 - can not ping to each other,
                 - can not ping to the ZoneDirector,
                 - can not ping to an IP address of ZD's non-default subnet
             when the feature 'Wireless Client Isolation' is enabled.
             This test is confirmed via a ping test and the addresses acquired on the clients.
             This test can support both 'g' and 'n' standards.

Product Line: ZoneDirector

Test_bed_type: ZoneDirector Test Bed

References

Test_ID/Customer_bug_ID:
     - ZD_CLIENT_ISOLATION_0001

Pre-requisite:
     - At least 2 clients supporting 11g
     - There must be at least one ZF7942 and/or ZF2925 and/or ZF2942

Configuration and Parameters:
     {'target_station': 'ip address of target station',
      'active_ap': 'mac address (NN:NN:NN:NN:NN:NN)of target ap which client will associate to',
      'radio_mode':'wireless mode on client  This value must be 'g' or n',
      'ip_of_non_default_subnet':'An IP that does not belong to the subnet 192.168.0.0/24.',
      'restricted_ip_list':'List of IP addresses that are restricted from clients'}

Test Procedure:
     - Config:
         + Make sure that the testbed has at least 2 clients.
         + Look for the target station and remove all WLAN(s) on that station.
         + Look for another station (destination station) and remove all WLAN(s) on that station.
         + Remove all configuration on the ZoneDirector.
         + Look for the active AP(2925, 2942 or 7942).
         + Get the current restricted subnet list.
         + Set the non-default subnet values to the restricted subnets.
     - Test:
         + Create a WLAN on the ZoneDirector.
         + Create a WLAN profile on the target station.
         + Make sure that the target station associates successfully.
         + Verify if the target station can get the IP and the MAC addresses.
         + Create a WLAN profile on the destination station.
         + Make sure that the destination station associates successfully.
         + Verify if the destination station can get the IP and the MAC addresses.
         + If the radio mode is not empty(using 7942),
           verify information of the target station shown on the Zone Director(IP, radio mode...)
         + Ping from the target station to another client, make sure that this ping fails.
         + Ping from the target station to the ZoneDirector, make sure that this ping fails.
         + Ping from the target station to the ZD's non-default subnet ip
           specified by the parameter 'ip_of_non_default_subnet', make sure that this ping fails.
     - Cleanup:
         + Remove all configuration on the ZoneDirector.
         + Set the restricted subnet to their original values.
         + Remove all WLAN profiles on the target station. Make sure that it completely disconnects from the WLAN.
         + Remove all WLAN profiles on the destination station. Make sure that it completely disconnects from the WLAN.

Observable Result:
     - A WLAN is created.
     - The target and destination stations asscociate and get IP and MAC addresses but can not ping to each other.
     - The target and destination stations disconnect from the WLAN.

Pass/Fail Criteria (including pass/fail messages)
- The test case passes if all of the verification steps in the test case are met.

How it was tested:
     - During the ping, disable the feature 'Wireless Client Isolation', the script must return FAIL.
     - Remove the non-default subnet on the ZoneDirector, the script should return FAIL.
     - Choose a 'g' client for the 'n' testscript, the script must return FAIL.

"""

import os
import re
import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_Wireless_Client_Isolation_For_Specific_AP(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_station': 'ip address of target station',
                           'active_ap': 'MAC address or symbolic name of target ap which client will associate to',
                           'radio_mode':'wireless mode on client  This value must be g or n',
                           'ip_of_non_default_subnet':'An IP that does not belong to the subnet 192.168.0.0/24.',
                           'restricted_ip_list':'List of IP addresses that are restricted from clients'}

    def config(self, conf):
        # Testing parameters
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                                     'sta_encryption': 'none', 'ras_addr': '', 'password': '', 'ad_domain': '',
                                     'ad_port': '', 'ssid': 'wlan_client_isolation', 'key_string': '',
                                     'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'wpa_ver': '',
                                     'ras_secret': '', 'use_client_isolation':True}
        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.destination_station = None
        self.target_station = None
        self.restricted_subnet_list = None
        self.zd_ip_addr = self.testbed.components['ZoneDirector'].ip_addr
        self.non_default_subnet_ip = conf['ip_of_non_default_subnet']
        self.radio_mode = conf['radio_mode']

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

        # Find the active AP object
        self.active_ap = tconfig.get_testbed_active_ap(self.testbed, conf['active_ap'], "Active AP")

        logging.info("Get the current restricted subnets.")
        self.restricted_subnet_list = self.testbed.components['ZoneDirector'].get_restricted_subnets()

        # Set the restricted subnets.
        logging.info("Set the list '%s' the restricted subnets." % conf['restricted_ip_list'])
        self.testbed.components['ZoneDirector'].set_restricted_subnets(conf['restricted_ip_list'])

    def test(self):
        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan_cfg)
        #JLIN@20081219 wait for ZD deploy setting to AP
        time.sleep(10)
        # Determine DUT AP (active_ap)
        # and turn-off wlan on non-active AP to ensure wireless client only associate to DUT AP
        for ap in self.testbed.components['AP']:
            if ap is not self.active_ap:
                logging.info("Remove all WLAN on non-active AP %s" % ap.get_base_mac())
                ap.remove_all_wlan()
        logging.info("Verify WLAN status on the active AP %s" % self.active_ap.get_base_mac())
        if not self.active_ap.verify_wlan():
            return ("FAIL", "WLAN %s on AP %s is not up" % (self.active_ap.ssid_to_wlan_if(self.wlan_cfg['ssid']),
                                                            self.active_ap.get_base_mac()))

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
        des_sta_wifi_ip_addr = None
        des_sta_wifi_mac_addr = None
        while time.time() - start_time < self.check_status_timeout:
            des_sta_wifi_ip_addr, des_sta_wifi_mac_addr = self.destination_station.get_wifi_addresses()
            if des_sta_wifi_mac_addr and des_sta_wifi_ip_addr and des_sta_wifi_ip_addr != "0.0.0.0":
                break
            time.sleep(1)
        logging.debug("Wifi IP: %s ---- Wifi MAC: %s" % (des_sta_wifi_ip_addr, des_sta_wifi_mac_addr))
        if not des_sta_wifi_mac_addr:
            msg = "Unable to get MAC address of the wireless adapter of the destination station %s" % \
                  self.destination_station.get_ip_addr()
            raise Exception(msg)
        if not des_sta_wifi_ip_addr:
            msg = "Unable to get IP address of the wireless adapter of the target station %s" % \
                  self.destination_station.get_ip_addr()
            raise Exception(msg)
        if des_sta_wifi_ip_addr == "0.0.0.0" or des_sta_wifi_ip_addr.startswith("169.254"):
            msg = "The target station %s could not get IP address from DHCP server" % \
                  self.destination_station.get_ip_addr()
            return ("FAIL", msg)

        if  self.radio_mode:
            logging.info("Verify information of the target station shown on the Zone Director")
            # Define the expected radio mode
            if self.radio_mode == 'g' or self.wlan_cfg['encryption'] in ['TKIP', 'WEP-64', 'WEP-128']:
                # 11n does not suport TKIP,WEP-64, WEP-128 encryption
                #JLIN@20081212 modified it for ZD8.0
                expected_radio_mode = '802.11b(|/)g'
            else:
                expected_radio_mode = '802.11g(|/)n'
            timed_out = False
            start_time = time.time()
            while True:
                all_good = True
                client_info_on_zd = None
                for client_info in self.testbed.components['ZoneDirector'].get_active_client_list():
                    logging.debug("Found info of a station: %s" % client_info)
                    if client_info['mac'].upper() == sta_wifi_mac_addr.upper():
                        client_info_on_zd = client_info
                        if client_info['status'] != 'Authorized':
                            if timed_out:
                                msg = "The station status shown on ZD was %s instead of 'Authorized'" % \
                                      client_info['status']
                                return ("FAIL", msg)
                            all_good = False
                            break
                        if self.wlan_cfg['auth'] == 'EAP' and client_info['ip'] != self.wlan_cfg['username']:
                            if timed_out:
                                msg = "The station username shown on ZD was %s instead of %s" % \
                                      (client_info['ip'], self.wlan_cfg['username'])
                                return ("FAIL", msg)
                            all_good = False
                            break
                        if self.wlan_cfg['auth'] != 'EAP' and client_info['ip'] != sta_wifi_ip_addr:
                            if timed_out:
                                msg = "The station wifi IP address shown on ZD was %s instead of %s" % \
                                      (client_info['ip'], sta_wifi_ip_addr)
                                return ("FAIL", msg)
                            all_good = False
                            break
                        if client_info['wlan'] != self.wlan_cfg['ssid']:
                            if timed_out:
                                msg = "The station's SSID shown on ZD was %s instead of %s" % \
                                      (client_info['wlan'], self.wlan_cfg['ssid'])
                                return ("FAIL", msg)
                            all_good = False
                            break
                        #JLIN@modified it for ZD8.0
                        #if client_info['radio'] != expected_radio_mode:
                        if not re.match(expected_radio_mode, client_info['radio']):
                            if timed_out:
                                msg = "The station's radio channel shown on ZD was %s instead of %s" % \
                                      (client_info['radio'], expected_radio_mode)
                                return ("FAIL", msg)
                            all_good = False
                            break
                        if client_info['apmac'] == '00:00:00:00:00:00':
                            if timed_out:
                                msg = "MAC address of the active AP shown on ZD was incorrect (%s)" % client_info['apmac']
                                return ("FAIL", msg)
                            all_good = False
                            break
                # End of for
                # Quit the loop if everything is good
                if client_info_on_zd and all_good: break
                # Otherwise, sleep
                time.sleep(1)
                timed_out = time.time() - start_time > self.check_status_timeout
                # And report error if the info is not available
                if not client_info_on_zd and timed_out:
                    msg = "Zone Director didn't show any info about the target station while it had been associated"
                    return ("FAIL", msg)
                # Or give it another try
            # End of while

        # Ping from the target station to another client, make sure that this ping fails.
        logging.info("Ping to %s from the target station (timeout: %s)" % (self.destination_station.get_ip_addr(),
                                                                           self.ping_timeout))
        ping_result = self.target_station.ping(des_sta_wifi_ip_addr, self.ping_timeout * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Correct behavior")
        else:
            logging.info("Ping OK. Incorrect behavior")
            return ("FAIL", "The target station could send traffic while the client isolation is enabled.")

        # Ping from the target station to the ZoneDirector, make sure that this ping fails.
        logging.info("Ping to ZoneDirector from the target station (timeout: %s)" % (self.ping_timeout))
        ping_result = self.target_station.ping(self.zd_ip_addr, self.ping_timeout * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Correct behavior")
        else:
            logging.info("Ping OK. Incorrect behavior")
            return ("FAIL", "The target station could send traffic to the ZoneDirector while the client isolation is enabled.")

        # Ping from the target station to a station not in the default subnet, make sure that this ping fails.
        logging.info("Ping to the ip '%s' from the target station (timeout: %s)" %
                     (self.non_default_subnet_ip, self.ping_timeout))
        ping_result = self.target_station.ping(self.non_default_subnet_ip, self.ping_timeout * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Correct behavior")
        else:
            logging.info("Ping OK. Incorrect behavior")
            return ("FAIL", "The target station could send traffic to the station with ip '%s'." %
                    self.non_default_subnet_ip)

        return ("PASS", "")

    def cleanup(self):
        logging.info("Remove all the configuration on the Zone Director")
        #self.testbed.components['ZoneDirector'].remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        # Set the restricted subnets to origin.
        if self.restricted_subnet_list:
            logging.info("Set the restricted subnets to their original values '%s'." % self.restricted_subnet_list)
            self.testbed.components['ZoneDirector'].set_restricted_subnets(self.restricted_subnet_list)

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

