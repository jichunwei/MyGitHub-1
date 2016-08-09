# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_ZeroIT_8BSSIDs Test class tests the ability of a station to associate with 8BSSIDs provided in Zero-IT tool

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'ip':'IP address to ping',
                    'target_station':'ip address of target station',

   Result type: PASS/FAIL
   Results: PASS: target station is exactly configured with 8 wlan profiles using zero-it,
                  it can associate to each WLAN, ping to a destination successfully and
                  information is shown correctly in ZD
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - On the Zone Director, remove all configuration about WLANs, users, authentication servers, active clients,
         all generated certificates, and generated PSKs on the ZD
   2. Test:
       - On the Zone Director, configure 8 WLANs with given security setting.
       - On the wireless client, configure the Ethernet interface with an IP address that is in the same
         subnet with the ZD
       - Use a browser and access to the activation URL provided to download Zero-IT tool. Use the given username
         and password to pass authentication.
       - Execute the Zero-IT tool on the wireless client.
       - Verify if the client is exactly configured with 8 wlans using Zero-IT tool
       - Verify if the client can access to each WLAN.
       - Do a ping to make sure traffic gets forwarded.
       - Verify if the ZD shows correct information about the connected station when it associates to each WLAN.
   3. Cleanup:
       - Remove all wlan configuration on ZD.
       - Remove wireless profiles on remote wireless STA

   How it is tested?
       - While the test is running, right after the local user is created on ZD, open another browser to ZD and
         remove that user. The script should report that Zero-IT tool cannot be downloaded because credential is invalid
       - Right after the Zero-IT tool is installed on the client, browse to ZD's WebUI and remove the WLAN. The script
         should report that it cannot connect to the WLAN.
"""

import os
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import Ratutils as utils


class ZD_ZeroIT_8BSSIDs(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'ip':'IP address to ping',
                           'target_station':'ip address of target station'}

    def config(self, conf):
        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.ip_addr = conf['ip']

        self.zd_ip_addr = self.testbed.components['ZoneDirector'].ip_addr
        self.sta_ip_addr = self.get_station_download_ip_addr()
        self.sta_net_mask = utils.get_subnet_mask(self.zd_ip_addr, False)
        self.activate_url = self.testbed.components['ZoneDirector'].get_zero_it_activate_url()

        self.wlan_cfg = {'username': 'ras.local.user', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                         'sta_encryption': 'none', 'ras_addr': '', 'password': 'ras.local.user', 'ad_domain': '',
                         'ad_port': '', 'ssid': '', 'key_string': '', 'sta_wpa_ver': '', 'use_radius': False,
                         'wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'ras_secret': '', 'use_zero_it': True}

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

    def test(self):
        logging.info("Create a user on the ZD")
        self.testbed.components['ZoneDirector'].create_user(self.wlan_cfg['username'], self.wlan_cfg['password'])

        logging.info("Configure 8 BSSIDs on the Zone Director")
        first_ssid = "rat_zeroit_bssid_wlan_1"
        self.wlan_cfg['ssid'] = first_ssid
        self.testbed.components['ZoneDirector'].cfg_wlan(self.wlan_cfg)

        # Create 7 wlans by cloning the first wlan
        i = 0
        while i < 7:
            ssid = "rat_zeroit_bssid_wlan_%d" % (i + 2)
            self.wlan_cfg['ssid'] = ssid
            self.testbed.components['ZoneDirector'].clone_wlan(first_ssid, ssid)
            time.sleep(2)
            i = i + 1

        logging.info("Use zero-it tool to configure 8 WLAN profiles on the target station %s" %
                     self.target_station.get_ip_addr())
        self.target_station.cfg_wlan_with_zero_it(self.target_station.get_ip_addr(), self.sta_ip_addr,
                                                 self.sta_net_mask, self.wlan_cfg['auth'], self.wlan_cfg['use_radius'],
                                                 self.activate_url, self.wlan_cfg['username'],
                                                 self.wlan_cfg['password'], "")

        time.sleep(4)
        logging.info("Make sure that wlan list on the ZD has the same length as wlan profile list on the station.")
        zd_wlan_list = self.testbed.components['ZoneDirector'].get_wlan_list()
        sta_wlan_list = self.target_station.get_wlan_profile_list()

        if len(zd_wlan_list) != len(sta_wlan_list):
            return ["FAIL", "The total of wlan profiles on the station is different from that on the ZD."]

        # Make sure that name of each ssid on the station is the same as the one on the ZD
        for wlan in zd_wlan_list:
            if not wlan in sta_wlan_list:
                logging.debug("Wlan list on the ZD: %s" % str(zd_wlan_list))
                logging.debug("Wlan list on the station: %s" % str(sta_wlan_list))
                return ["FAIL", "The wlan with SSID %s is not configured on the station" % wlan]
        logging.info("Wlan profile information on the ZD is the same as the one on the ZD")

        # Verify that station can associate to 8 wlans
        for wlan in zd_wlan_list:
            logging.info("Make sure that station can associate to the wlan with SSID %s successfully" % wlan)
            self.target_station.connect_to_wlan(wlan)
            time.sleep(2)
            res, msg = self._verifyAssociatedClient(wlan)
            if res == "FAIL":
                return [res, msg]

        return ["PASS", ""]

    def cleanup(self):
        logging.info("Remove all the WLANs on the Zone Director")
        #self.testbed.components['ZoneDirector'].remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        if self.target_station:
            logging.info("Remove all WLAN profiles on the remote station")
            self.target_station.remove_all_wlan()

            logging.info("Make sure the target station disconnects from the wireless networks")
            start_time = time.time()
            current_time = start_time
            while current_time - start_time <= self.check_status_timeout:
                if self.target_station.get_current_status() == "disconnected":
                    break
                time.sleep(1)
                current_time = time.time()
            if current_time - start_time > self.check_status_timeout:
                raise Exception("The station did not disconnect from wireless network within %d seconds" %
                                self.check_status_timeout)
        logging.info("-------- FINISHED --------")

    def _verifyAssociatedClient(self, ssid):
        """
        Verify information of target station when it associates to the wlan successfully
        """
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "connected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                raise Exception("The station did not connect to wireless network within %d seconds" %
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

        logging.info("Verify information of the target station shown on the Zone Director")
        retry = 5
        client_info_on_zd = None
        start_time = time.time()
        current_time = start_time
        while current_time - start_time <= self.check_status_timeout:
            for client in self.testbed.components['ZoneDirector'].get_active_client_list():
                # Only verify the target station
                if client['mac'].upper() == sta_wifi_mac_addr.upper():
                    if client['status'] != 'Authorized':
                        if not retry:
                            logging.debug('Active client information on ZD %s' % client)
                            return ("FAIL", "The station status shown on ZD is not 'Authorized'")
                        retry = retry - 1
                        break
                    if client['wlan'] != ssid:
                        if not retry:
                            logging.debug('Active client information on ZD %s' % client)
                            return ("FAIL", "The station's SSID shown on ZD is not %s" % ssid)
                        retry = retry - 1
                        break

                    # All info are satisfied, this is the expected client
                    client_info_on_zd = client
                    break

            if client_info_on_zd: break

            time.sleep(1)
            current_time = time.time()
        # End of while not timeout

        if not client_info_on_zd:
            if self.target_station.get_current_status() == "connected":
                msg = "Zone Director didn't show any info about the station (with MAC %s)" % sta_wifi_mac_addr
                msg += " while it had been associated"
            else:
                msg = "The station didn't associate after %s seconds" % self.check_status_timeout
            return ("FAIL", msg)

        logging.info("Try to ping to %s from the target station %s" % (self.ip_addr, self.target_station.get_ip_addr()))
        ping_result = self.target_station.ping(self.ip_addr, self.ping_timeout * 1000)
        if ping_result.find("Timeout") != -1:
            logging.info("Ping FAILED. Incorrect behavior.")
            return ("FAIL", "The target station could not send traffic.")
        else:
            logging.info("Ping OK. Correct behavior.")

        return ["", ""]

    def get_station_download_ip_addr(self, vlan_id="301"):
        vlan_ip_table = self.testbed.components['L3Switch'].get_vlan_ip_table()
        ip_addr = [ ll['ip_addr'] for ll in vlan_ip_table if ll['vlan_id'] == vlan_id]
        return ".".join("".join(ip_addr).split(".")[:-1]) + ".50"



        


