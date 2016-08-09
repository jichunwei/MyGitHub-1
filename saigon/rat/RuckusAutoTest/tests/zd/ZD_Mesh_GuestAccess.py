# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_Mesh_GuestAccess Test class tests the ability of a station to associate with an AP under ZD's control
with open security configuration and Guest Pass authentication mechanism under Mesh Topology.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'ip': 'IP address to ping',
                    'target_station': 'ip address of target station',
                    'use_guest_auth': 'Use Guest Pass access authentication or not',
                    'use_tou': 'Use Terms Of Use or not',
                    'redirect_url': 'Use this redirect URL'
   Result type: PASS/FAIL/ERROR
   Results: PASS: target station can associate, pass WebAuth, ping to a destination successfully and
                  information is shown correctly in ZD and AP
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Initialize Client's parameter
       - Enable Mesh
       - Find active AP
       - Select Mesh uplink
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
       - Remove all guest passes if existed
   2. Test:
       - Configure a WLAN on the ZD with open security setting
       - Configure Guest Access policy and configure a user which will be used to generate guest pass
       - Open another browser, browse to the Guest Pass Generation page and generate a guest pass
       - Disable other service wlan except the one under test
       - Configure the target station with given security setting
       - Wait until it gets associated and get IP and MAC addresses of the wireless adapter
       - Do a ping to make sure the AP doesn't forward the traffic from the station
       - Verify if the ZD shows correct information about the connected station
       - Do Guest authentication from the station
       - Do a ping again to make sure traffic gets forwarded
       - Verify if the ZD shows correct information about the connected station one more time
   3. Cleanup:
       - Remove all wlan configuration and generated guest passes on ZD
       - Remove wireless profile on remote wireless STA
       - Verify if wireless station is completely disconnected after removing the wireless profile

   How it is tested?
       - While the test is running, right after the guest pass is generated, go to the table Generated Guest Pass
         and remove it. The script should report that it is unable to do the Guest authentication on the remote
         station because the pass has been expired or invalid
       - After the client has done the authentication successfully, go to the table Active Clients and delete that
         user. The script should report that the ZD has incorrect info about the client

"""

import os
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_Mesh_GuestAccess(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'ip': 'IP address of server that station pings to',
                           'target_station': 'ip address of target station',
                           'active_ap':'mac address (NN:NN:NN:NN:NN:NN)of target ap which client will associate to',
                           'use_guest_auth': 'Use Guest Pass access authentication or not',
                           'use_tou': 'Use Terms Of Use or not',
                           'redirect_url': 'Use this redirect URL',
                           'topology':'Mesh topology, possible values are root, or root-mesh',
                           'model': 'AP model (optional)'}

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']

        # Define test parameters
        # Security setting used for the test is open-none
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                         'sta_encryption': 'none', 'ras_addr': '', 'password': '', 'use_guest_access': True,
                         'ad_domain': '', 'ad_port': '', 'ssid': 'rat-guest-access-testing', 'key_string': '',
                         'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'wpa_ver': '', 'ras_secret': ''}
        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.ip_addr = conf['ip']
        self.use_guest_auth = conf['use_guest_auth']
        self.use_tou = conf['use_tou']
        self.target_station = None

        self.redirect_url = conf['redirect_url']

        self.username = "ruckus"
        self.password = "ruckus"
        if self.use_guest_auth:
            self.guest_name = "Bull Dog"
        else:
            self.guest_name = "guest"
        self.current_guest_access_policy = None
        self.current_guest_pass_policy = None

        logging.info("Enable mesh on the Zone Director")

        self.mesh_name = utils.make_random_string(32, "alpha")
        self.mesh_psk = utils.make_random_string(63, "alpha")
        self.testbed.enable_mesh(self.mesh_name, self.mesh_psk)


        # Find the active AP object
        self.active_ap = None
        for ap in self.testbed.components['AP']:
            if isinstance(ap, RuckusAP):
                if ap.get_base_mac().upper() == conf['active_ap'].upper():
                    self.active_ap = ap
        if not self.active_ap:
            raise Exception("Active AP not found in test bed")

        # Select the APs
        self.root_aps = []
        self.mesh_aps = []
        if not conf['topology']:
            # Verify all connected APs
            self.root_aps = self.testbed.mac_to_ap.keys()
        else:
            # Verify only some APs of a given model
            if not conf['model']:
                raise Exception("Not found parameter 'model'")
            #when the topology is "root" mark "active_ap" to be Root
            if conf['topology'].lower() == "root":
                for mac, ap in self.testbed.mac_to_ap.iteritems():
                    if ap.get_device_type().lower() == conf['model'].lower():
                        if mac.lower() == self.active_ap.get_base_mac().lower():
                            self.root_aps = [mac]
                            break
                if not self.root_aps:
                    raise Exception("There is no AP with model '%s' in the testbed" % conf['model'])
            elif conf['topology'].lower() == "root-mesh":
                mesh_temp = ""
                for mac, ap in self.testbed.mac_to_ap.iteritems():
                    if ap.get_device_type().lower() == conf['model'].lower():
                        if mac.lower() == self.active_ap.get_base_mac().lower():
                            mesh_temp = mac
                        else:
                            self.root_aps.append(mac)
                if mesh_temp:
                    self.mesh_aps = [(mesh_temp, self.root_aps)]
                if not self.root_aps or not self.mesh_aps:
                    raise Exception("There is not AP with model '%s' in the testbed" % conf['model'])
            else:
                raise Exception("Invalid topology '%s'" % conf['topology'])


        logging.info("Form mesh network by configuring Switch ports")
        self.testbed.form_mesh(self.root_aps, self.mesh_aps)


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

        logging.info("Remove all configuraton on the Zone Director")
        self.zd.remove_all_cfg()

        logging.info("Remove all Guest Passes created on the Zone Director")
        self.zd.remove_all_guestpasses()

        logging.info("Record current Guest Access Policy on the ZD")
        self.current_guest_access_policy = self.zd.get_guestaccess_policy()

        logging.info("Record current Guest Password Policy on the ZD")
        self.current_guest_pass_policy = self.zd.get_guestpass_policy()

    def test(self):


        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        self.zd.cfg_wlan(self.wlan_cfg)

        logging.info("Configure Guest Access policy on the Zone Director")
        self.zd.set_guestaccess_policy(use_guestpass_auth = self.use_guest_auth,
                                       use_tou = self.use_tou,
                                       redirect_url = self.redirect_url)
        logging.debug("New Guest Access Policy use_guestpass_auth=%s --- use_tou=%s --- redirect_url=%s" %
                      (self.use_guest_auth, self.use_tou, self.redirect_url))

        if self.use_guest_auth:
            logging.info("Create a user on the Zone Director")
            self.zd.create_user(self.username, self.password)

            logging.info("Configure Guest Password policy on the Zone Director")
            self.zd.set_guestpass_policy(auth_serv = "Local Database")

            logging.info("Generate a Guest Pass on the ZD")
            guest_pass, expired_time = self.zd.generate_guestpass(self.username, self.password,
                                                                  self.guest_name, "1", "Days")
        else:
            guest_pass = ""

        # Find the active AP be it MAP or Root
        # And turn-off all service WLANs on the non-active APs to ensure wireless client only associate to the active AP
        # Leave wlan8 and wlan9 alone, if active_ap is MAP there will be one MAP connected to one of multiple Roots randomly
        for ap in self.testbed.components['AP']:
            if ap is not self.active_ap:
                logging.info("Remove all WLANs on non-active AP %s" % ap.get_base_mac())
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
        while time.time() - start_time < 15:
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

        logging.info("Ping to %s from the target station" % self.ip_addr)
        ping_result = self.target_station.ping(self.ip_addr, 5 * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Correct behavior")
        else:
            logging.info("Ping OK. Incorrect behavior")
            return ("FAIL", "The target station could send traffic while it was not authorized by ZD")

        logging.info("Verify information of the target station shown on the Zone Director")
        timed_out = False
        start_time = time.time()
        while True:
            all_good = True
            client_info_on_zd = None
            for client_info in self.zd.get_active_client_list():
                logging.debug("Found info of a station: %s" % client_info)
                if client_info['mac'].upper() == sta_wifi_mac_addr.upper():
                    client_info_on_zd = client_info
                    if client_info['status'] != 'Unauthorized':
                        if timed_out:
                            msg = "The station status was %s instead of 'Unauthorized' before doing GuestAuth" % \
                                  client_info['status']
                            return ("FAIL", msg)
                        all_good = False
                        break
                    if client_info['ip'] != sta_wifi_ip_addr:
                        if timed_out:
                            msg = "The station wifi IP address was %s instead of %s" % \
                                  (client_info['ip'], sta_wifi_ip_addr)
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
                msg = "Zone Director didn't show any info about the target station"
                return ("FAIL", msg)
            # Or give it another try
        # End of while

        logging.info("Perform Guest Pass authentication on the target station %s" % self.target_station.get_ip_addr())
        arg = tconfig.get_guest_auth_params(self.zd, guest_pass, self.use_tou, self.redirect_url)
        self.target_station.perform_guest_auth(arg)

        logging.info("Try to ping to %s from the target station %s one more time" % (self.ip_addr, self.target_station.get_ip_addr()))
        ping_result = self.target_station.ping(self.ip_addr, self.ping_timeout * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Incorrect behavior")
            return ("FAIL", "The target station could not send traffic after doing Guest authentication")
        else:
            logging.info("Ping OK. Correct behavior")

        logging.info("Verify information of the target station shown on the Zone Director one more time")
        timed_out = False
        start_time = time.time()
        while True:
            all_good = True
            client_info_on_zd = None
            for client_info in self.zd.get_active_client_list():
                logging.debug("Found info of a station: %s" % client_info)
                if client_info['mac'].upper() == sta_wifi_mac_addr.upper():
                    client_info_on_zd = client_info
                    if client_info['status'] != 'Authorized':
                        if timed_out:
                            msg = "The station status was %s instead of 'Authorized' after doing GuestAuth" % \
                                  client_info['status']
                            return ("FAIL", msg)
                        all_good = False
                        break
                    # After being authenticated, the station's IP will change to username
                    if client_info['ip'] != self.guest_name:
                        if timed_out:
                            msg = "The station's username shown on ZD was %s instead of %s" % \
                                  (client_info['ip'], self.guest_name)
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

        return ("PASS", "")

    def cleanup(self):
        logging.info("Remove all the WLANs on the Zone Director")
        #self.zd.remove_all_cfg()

        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        #logging.info("Remove all Guest Passes created on the Zone Director")
        #self.zd.remove_all_guestpasses()

        if self.current_guest_access_policy:
            logging.info("Restore Guest Access Policy to original configuration on ZD")
            self.zd.set_guestaccess_policy(**self.current_guest_access_policy)

        if self.current_guest_pass_policy:
            logging.info("Restore Guest Password Policy to original configuration on ZD")
            self.zd.set_guestpass_policy(**self.current_guest_pass_policy)

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

        logging.info("Restore the mesh to original configuration")
        all_root_aps = self.testbed.mac_to_ap.keys()
        all_mesh_aps = []
        self.testbed.form_mesh(all_root_aps, all_mesh_aps)

