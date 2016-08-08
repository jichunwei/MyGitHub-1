# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_Dynamic_PSK_Expiration Test class tests the ability of the ZoneDirector to generate PSKs and
             manage the expiration time of them properly.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'ip': 'IP address to ping',
                    'target_station': 'IP address of target station',
                    'expiration_time': 'PSK expiration time'
   Result type: PASS/FAIL
   Results: PASS: target station can associate to the WLAN, ping to a destination successfully and
                  information is shown correctly in ZD
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
       - Create a local user and choose Local Database for Zero-IT activation
       - Configure PSK Expiration time to the given value
       - Configure a WLAN on the ZD using WPA/AES with Zero-IT and Dynamic-PSK enabled
   2. Test:
       - On the wireless client, configure the Ethernet interface with an IP address that is in the same
         subnet with the ZD
       - Use a browser and access to the activation URL provided to download Zero-IT tool. Use the local username
         and password created on ZD to authenticate.
       - Remove the newly created IP interface.
       - Verify if a new PSK has been created on the Generate PSKs table. Make sure that the expiration time
         is correct.
       - Execute the Zero-IT tool on the wireless client.
       - Verify if the client can access to the WLAN configured in the Zero-IT tool.
       - Verify if the client can ping to the given IP address.
       - Verify if the ZD shows correct information about the connected station.
       - Update system on the ZoneDirector to a time that is later than the expiration time of the PSK.
       - Remove the WLAN profiles on the target station.
       - Rerun the Zero-IT tool.
       - Verify that the station can associate to the WLAN.
       - Verify that it cannot ping the given IP address.
       - Verify if the status of the station is "PSK Expired" in the Currently Active Clients table
         on the ZoneDirector.
   3. Cleanup:
       - Remove all configuration on ZD.
       - Remove all wireless profiles on the target station.

   How it is tested?
       - While the test is running, login to the ZoneDirector and change the local username/password. The
         test must report that it cannot download Zero-IT tool.
       - After the Zero-IT tool is downloaded, login the the ZoneDirector and remove the generated PSK. The
         test must report that the station cannot associate to the WLAN.
"""

import os
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import Ratutils as utils

class ZD_Dynamic_PSK_Expiration(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'ip': 'IP address to ping',
                           'target_station': 'ip address of target station',
                           'expiration_time': 'PSK expiration time'}

    def config(self, conf):
        # Record current time of the PC in order to set back to it after all
        self.current_sys_time = time.time()
        self.start_sys_clock = time.clock()

        # Define configuration variables
        self.wlan_cfg = dict(ssid = "rat-dynamic-psk-expiration", auth = "PSK", wpa_ver = "WPA", encryption = "AES",
                             sta_auth = "PSK", sta_wpa_ver = "WPA", sta_encryption = "AES",
                             key_index = "" , key_string = "1234567890",
                             username = "ras.local.user", password = "ras.local.user", ras_addr = "", ras_port = "",
                             ras_secret = "", use_radius = False, use_zero_it = True, use_dynamic_psk = True)
        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.target_ip = conf['ip']
        self.expiration_time = conf['expiration_time']
        self.expiration_time_s = {'One day': 86400, 'One week': 604800, 'Two weeks': 1209600,
                                  'One month': 2592000, 'Two months': 5184000, 'Three months': 7776000,
                                  'Half a year': 15768000, 'One year': 31536000, 'Two years': 63072000}

        # Calculate an IP address that stays in the same subnet as the Zone Director
        # This address will be configured to the Ethernet interface of the target
        # station temporarily when downloading Zero-IT tool
        self.zd_ip_addr = self.testbed.components['ZoneDirector'].ip_addr
        self.sta_ip_addr = self.get_station_download_ip_addr()
        self.sta_net_mask = utils.get_subnet_mask(self.zd_ip_addr, False)
        self.activate_url = self.testbed.components['ZoneDirector'].get_zero_it_activate_url()

        logging.info("Remove all configurations on the Zone Director")
        #self.testbed.components['ZoneDirector'].remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        # Find the target station object and remove all Wlan profiles
        self.target_station = None
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
            raise Exception("Target station %s not found" % conf['target_station'])

        logging.info("Log current Dynamic PSK configuration on Zone Director")
        self.dynpsk_cfg = self.testbed.components['ZoneDirector'].get_dynamic_psk_cfg()

        logging.info("Create a user on the ZD")
        self.testbed.components['ZoneDirector'].create_user(self.wlan_cfg['username'], self.wlan_cfg['password'])

        logging.info("Configure a WLAN %s with Zero-IT and Dynamic-PSK enabled on the Zone Director" %
                     self.wlan_cfg['ssid'])
        self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan_cfg)

        logging.info("Configure new Dynamic PSK expiration time on the Zone Director")
        self.testbed.components['ZoneDirector'].set_dynamic_psk_cfg(self.expiration_time)

    def test(self):
        logging.info("Download Zero-IT tool on the target station %s" % self.target_station.get_ip_addr())
        tool_path = self.target_station.download_zero_it(self.target_station.get_ip_addr(), self.sta_ip_addr,
                                                       self.sta_net_mask, self.activate_url,
                                                       self.wlan_cfg['username'], self.wlan_cfg['password'])

        logging.info("Verify the newly generated PSK")
        psks = self.testbed.components['ZoneDirector'].get_all_generated_psks_info()
        if len(psks) == 0:
            return ("FAIL", "No PSK was created on the Zone Director after downloading the ZeroIT tool")
        if len(psks) > 1:
            return ("FAIL", "More than one PSK were created after downloading the ZeroIT tool")
        psk = psks[0]
        if psk['user'] != self.wlan_cfg['username']:
            return ("FAIL", "The user name of the PSK is %s instead of %s" % (psk['user'],
                                                                              self.wlan_cfg['username']))
        # Validate the expiration time
        created_time_s = time.mktime(time.strptime(psk['created_time'], "%Y/%m/%d %H:%M:%S"))
        expired_time_s = time.mktime(time.strptime(psk['expired_time'], "%Y/%m/%d %H:%M:%S"))
        delta_time = expired_time_s - created_time_s
        if delta_time != self.expiration_time_s[self.expiration_time]:
            msg = "The duration from %s to %s is not the same as configured on PSK Expiration (%s or %s seconds)" % \
                  (psk['created_time'], psk['expired_time'],
                   self.expiration_time, self.expiration_time_s[self.expiration_time])
            return ("FAIL", msg)

        logging.info("Execute the Zero-IT tool on the target station")
        self.target_station.execute_zero_it(tool_path, self.wlan_cfg['ssid'], self.wlan_cfg['auth'],
                                          self.wlan_cfg['use_radius'])

        # Make sure it connects to the wireless network
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "connected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                msg = "The station did not connect to the wireless network after running the ZeroIT tool"
                raise Exception(msg)

        logging.info("Renew IP address of the wireless adapter on the target station")
        self.target_station.renew_wifi_ip_address()

        logging.info("Ping to %s from the target station" % self.target_ip)
        ping_result = self.target_station.ping(self.target_ip, 10 * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Incorrect behavior")
            return ("FAIL", "The target station could not send traffic after %s seconds" % self.ping_timeout)
        else:
            logging.info("Ping OK. Correct behavior")

        logging.info("Get IP and MAC addresses of the wireless adapter on the target station %s" %
                     self.target_station.get_ip_addr())
        sta_wifi_ip_addr, sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
        logging.info("Wifi IP: %s ---- Wifi MAC: %s" % (sta_wifi_ip_addr, sta_wifi_mac_addr))
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

        logging.info("Verify information of the target station shown on the Zone Director")
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
                    if client_info['ip'] != self.wlan_cfg['username']:
                        if timed_out:
                            msg = "The station username shown on ZD was %s instead of %s" % \
                                  (client_info['ip'], self.wlan_cfg['username'])
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

        logging.info("Verify the PSK one more time")
        psks = self.testbed.components['ZoneDirector'].get_all_generated_psks_info()
        if len(psks) == 0:
            return ("FAIL", "The PSK was removed unexpectedly")
        if len(psks) > 1:
            return ("FAIL", "One more PSK was created unexpectedly")
        psk = psks[0]
        if psk['user'] != self.wlan_cfg['username']:
            msg = "The user name of the PSK was %s instead of %s" % (psk['user'], self.wlan_cfg['username'])
            return ("FAIL", msg)
        if psk['mac'].upper() != sta_wifi_mac_addr.upper():
            return ("FAIL", "The MAC of the PSK was %s instead of %s" % (psk['mac'], sta_wifi_mac_addr))

        logging.info("Change system time on the Zone Director to make the PSK expired")
        # Change the clock on the PC to the expiration time of the PSK
        utils.set_local_time(psk['expired_time'])
        # And sync time on the ZoneDirector to the PC time
        self.testbed.components['ZoneDirector'].get_current_time(True)
        # Wait a few seconds to make the PSK expired
        time.sleep(5)

        logging.info("Remove all WLAN profiles on the target station")
        self.target_station.remove_all_wlan()
        # Make sure it disconnects from the wireless network
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "disconnected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                raise Exception("The station did not disconnect from wireless network within %d seconds" %
                                self.check_status_timeout)

        logging.info("Execute the Zero-IT tool on the target station one more time")
        self.target_station.execute_zero_it(tool_path, self.wlan_cfg['ssid'], self.wlan_cfg['auth'],
                                          self.wlan_cfg['use_radius'])
        # Make sure it connects to the wireless network
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "connected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                msg = "The station did not connect to the wireless network after running the ZeroIT tool"
                raise Exception(msg)

        logging.info("Verify information of the target station shown on the Zone Director one more time")
        timed_out = False
        start_time = time.time()
        while True:
            all_good = True
            client_info_on_zd = None
            for client_info in self.testbed.components['ZoneDirector'].get_active_client_list():
                logging.debug("Found info of a station: %s" % client_info)
                if client_info['mac'].upper() == sta_wifi_mac_addr.upper():
                    client_info_on_zd = client_info
                    if client_info['status'] != 'PSK Expired':
                        if timed_out:
                            msg = "The station status shown on ZD was %s instead of 'PSK Expired'" % \
                                  client_info['status']
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

        logging.info("Ping to %s from the target station one more time" % self.target_ip)
        ping_result = self.target_station.ping(self.target_ip, 10 * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Correct behavior")
        else:
            logging.info("Ping OK. Incorrect behavior")
            msg = "The target station could send traffic after its PSK had been expired"
            return ("FAIL", msg)

        return ("PASS", "")

    def cleanup(self):
        logging.info("Remove all the WLANs on the Zone Director")
        #self.testbed.components['ZoneDirector'].remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        logging.info("Restore PSK Expiration configuration on the Zone Director")
        self.testbed.components['ZoneDirector'].set_dynamic_psk_cfg(self.dynpsk_cfg)

        # Restore time on the PC and Zone Director to original time
        utils.set_local_time(self.current_sys_time + (time.clock() - self.start_sys_clock))
        self.testbed.components['ZoneDirector'].get_current_time(True)

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

    def get_station_download_ip_addr(self, vlan_id="301"):
        vlan_ip_table = self.testbed.components['L3Switch'].get_vlan_ip_table()
        ip_addr = [ ll['ip_addr'] for ll in vlan_ip_table if ll['vlan_id'] == vlan_id]
        return ".".join("".join(ip_addr).split(".")[:-1]) + ".50"
