# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script is use to test PMK Function with EAP-WPA2-TKIP or EAP-WPA2-AES

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'target_station': The target station ip address.
                                      This station should be an Windows XP SP2 with Broadcom wireless card.
                    'encryption_option': TKIP/AES (Optional). The test run default with AES
   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Base on test option, we will configure the active ap:
            + Configure the wlan (EAP-WPA2-TKIP or EAP-WPA2-AES) on Zone Director
   2. Test:
       - Associate target station to wlan of ZD system
            + Verify if there is a PMK key be created
            + Verify there is Radius traffic between ZD and server
       - Disconnect the station then reconect station to wlan of ZD system
            + Verify if there is no new PMK key be created
            + Verify there is Radius traffic between ZD and server
   3. Cleanup:
       - Return the original configuration

   How it is tested?

"""

import os
import time
import re
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.ZoneDirectorCLI import ZoneDirectorCLI

class ZD_PMK_Cache_Function(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector', 'LinuxPC']
    test_parameters = {'target_station': 'The target station ip address. \
                                          This station should be an Windows XP SP2 with Broadcom wireless card.',
                       'encryption_option': 'TKIP/AES (Optional). The test run default with AES'}

    def config(self, conf):
        # Define the testing parameters
        self._initTestParamesters(conf)
        # Setting the target station for testing
        self._cfgTargetStation()
        # Setting the Zone Director for testing
        self._cfgZoneDirector()

    def test(self):
        self._testPMKFunction()
        if self.errmsg: return ('FAIL', self.errmsg)

        return ('PASS', '')

    def cleanup(self):
        logging.info('Stop all sniffer on Linux server if running')
        if self.linux_server:
            self.linux_server.stop_sniffer()

        logging.info('Remove all testing configuration on the Zone Director')
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        # Remove all wlan configuration on target station
        if self.target_station:
            tconfig.remove_all_wlan_from_station(self.target_station)

    def _initTestParamesters(self, conf):
        self.target_station = None
        self.roaming_ap = None
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = None
        self.linux_server = self.testbed.components['LinuxServer']
        self.server_ip_addr = self.linux_server.ip_addr
        self.conf = conf
        self.ping_timeout = 150
        self.check_status_timeout = 180
        server_interface = self.linux_server.get_interface_name_by_ip(self.linux_server.ip_addr)
        self.params_for_sniffer = "-i %s udp port 1812 -s 1500" % server_interface

        # Define the testing wlan configuration
        ssid = 'PMK Cache Function - %s' % time.strftime("%H%M%S")
        self.wlan_cfg = dict(ssid = ssid, auth = "EAP", wpa_ver = "WPA2", encryption = "",
                             sta_auth = "EAP", sta_wpa_ver = "WPA2", sta_encryption = "",
                             key_index = "" , key_string = "",
                             username = "ras.eap.user", password = "ras.eap.user",
                             ras_addr = self.linux_server.ip_addr, ras_port = "1812",
                             ras_secret = "1234567890", use_radius = True)

        if conf.has_key('encryption_option') and conf['encryption_option']:
            encrypt_mode = conf['encryption_option'].upper()
            if encrypt_mode in ['TKIP', 'AES']:
                self.wlan_cfg['encryption'] = encrypt_mode
                self.wlan_cfg['sta_encryption'] = encrypt_mode
            else:
                msg = 'The test support encryption mode "TKIP" or "AES" but "%s"' % conf['encryption_option']
                logging.info(msg)
                raise Exception(msg)
        else:
            self.wlan_cfg['encryption'] = 'AES'
            self.wlan_cfg['sta_encryption'] = 'AES'

        # Create an ssh session to the Zone Director
        zdconfig = {'ip_addr':self.zd.ip_addr, 'username':self.zd.username, 'password':self.zd.password}
        self.zdcli = ZoneDirectorCLI(zdconfig)

    def _cfgTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                               , self.testbed.components['Station']
                                               , check_status_timeout = self.check_status_timeout
                                               , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])
        self.target_station_wifi_ip_addr = None
        self.target_station_wifi_macaddr = None

    def _cfgZoneDirector(self):
        logging.info("Remove all WLAN on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        logging.info("Configure Zone Director for testing")
        # Setting create wlan with appropriate authentication server
        if self.wlan_cfg['auth'] == "EAP":
            logging.info("Create an authentication server on the ZoneDirector")
            if self.wlan_cfg['use_radius']:
                self.zd.create_radius_server(self.wlan_cfg['ras_addr'],
                                         self.wlan_cfg['ras_port'],
                                         self.wlan_cfg['ras_secret'])
            else:
                logging.info("Create a user on the ZoneDirector")
                self.zd.create_user(self.wlan_cfg['username'], self.wlan_cfg['password'])

        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        self.zd.cfg_wlan(self.wlan_cfg)
        # Wait a moment for ZD to push config to the APs
        time.sleep(2)

    def _verifyStationAssociation(self):
        # Access the target station to Zone Director system
        msg = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_cfg, self.check_status_timeout)
        if msg:
            raise Exception(msg)

        # Verify the if client get the IP address successfully
        val1, val2, val3 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)
        if not val1:
            raise Exception(val3)
        else:
            self.target_station_wifi_ip_addr = val2
            self.target_station_wifi_macaddr = val3

    def _verifyPMKCacheInfo(self, expect_pmk = True):
        self.errmsg = ""
        pmk_count, pmk_info = self.zdcli.get_pmk_info()

        if expect_pmk and (not pmk_count or pmk_count == '0'):
            msg = "There is not PMK cache in the ZD"
            logging.info(msg)
            self.errmsg = msg

        elif not expect_pmk and pmk_count > '0':
            for pmk in pmk_info:
                if pmk['station'].lower() == self.target_station_wifi_macaddr.lower() \
                and pmk['auth_user'] == self.wlan_cfg['username']:
                    msg = 'The PMK key for station %s till exists [%s]'
                    msg = msg % (self.target_station_wifi_macaddr, repr(pmk))
                    logging.info(msg)
                    self.errmsg = msg

        elif expect_pmk and pmk_count > '0':
            for pmk in pmk_info:
                if pmk['station'].lower() == self.target_station_wifi_macaddr.lower() \
                and pmk['auth_user'] == self.wlan_cfg['username']:
                    msg = 'The PMK key for station %s exists [%s]'
                    msg = msg % (self.target_station_wifi_macaddr, repr(pmk))
                    logging.info(msg)
                    self.errmsg = ''
                    break
                else:
                    msg = 'There no PMK key for station %s' % self.target_station_wifi_macaddr
                    self.errmsg = msg

            if self.errmsg:
                logging.info(self.errmsg)

        return (pmk_count, pmk_info)

    def _verifyRadiusPacket(self, expect_radius_packet = True):
        self.errmsg = ""
        check_log_packet = self.linux_server.read_sniffer()
        logging.debug(repr(check_log_packet))
        radius_pkt_exist = None
        for line in check_log_packet:
            radius_pkt_exist = re.search('RADIUS', line)
            if radius_pkt_exist:
                break

        if expect_radius_packet and not radius_pkt_exist:
            self.errmsg = "There is no Radius Packet between the ZD and the Server"
        elif not expect_radius_packet and radius_pkt_exist:
            self.errmsg = "There is Radius Packet between the ZD and the Server"

    def _verifyIfAllAPConnected(self):
        # Verify if the APs is still connected on ZD
        start_time = time.time()
        while True:
            connected = 0
            aps_info = self.zd.get_all_ap_info()
            for ap in aps_info:
                if ap['status'].lower().startswith("connected"):
                    connected += 1
            if connected == len(self.testbed.components['AP']):
                break
            if time.time() - start_time > self.check_status_timeout:
                raise Exception("There are %d APs disconnecting from the ZD"
                                % (len(self.testbed.components['AP']) - connected))
            time.sleep(1)

    def _testPMKFunction(self):
        logging.info('Verify if there an PMK be created after target station connect to WLAN')
        # Start sniffer on linux server to verify the radius traffic between Zone Director and Server
        self.linux_server.start_sniffer(self.params_for_sniffer)

        # Access target station to Zone director and verify if it access successully
        self._verifyStationAssociation()

        # Verify if there is an entry of target station on Zone Director
        target_sta_info_on_zd = tmethod.get_active_client_by_mac_addr(self.target_station_wifi_macaddr, self.zd)
        if not target_sta_info_on_zd:
            msg = 'There is not information about client [%s] on Zond Director' % self.target_station_wifi_macaddr
            raise Exception(msg)

        # Verify there is an PMK entry for target station
        pmk_count_1, pmk_info_1 = self._verifyPMKCacheInfo()
        if self.errmsg or not pmk_count_1 or pmk_count_1 == '0' :
            return

        # Verify if there is any Radius packet between Zone Director and Server
        self.linux_server.stop_sniffer()
        self._verifyRadiusPacket()
        if self.errmsg:
            return

        logging.info('Verify if there is any new PMK be created after target station disconnect and reconnect to WLAN')

        # Remove all wlan configuration on station
        tconfig.remove_all_wlan_from_station(self.target_station)

        self.linux_server.start_sniffer(self.params_for_sniffer)

        self._verifyStationAssociation()

        target_sta_info_on_zd = tmethod.get_active_client_by_mac_addr(self.target_station_wifi_macaddr, self.zd)
        if not target_sta_info_on_zd:
            msg = 'There is not information about client [%s] on Zond Director' % self.target_station_wifi_macaddr
            raise Exception(msg)

        pmk_count_2, pmk_info_2 = self._verifyPMKCacheInfo()
        if self.errmsg or not pmk_count_2 or pmk_count_2 == '0':
            return

        if pmk_count_2 != pmk_count_1:
            msg = 'The PMK count is changed after station [%s] reconnect to WLAN [Before: %s - After: %s]'
            msg = msg % (self.target_station_wifi_macaddr, pmk_count_1, pmk_count_2)
            self.errmsg = msg
            return

        self.linux_server.stop_sniffer()
        self._verifyRadiusPacket()
        if self.errmsg:
            return

