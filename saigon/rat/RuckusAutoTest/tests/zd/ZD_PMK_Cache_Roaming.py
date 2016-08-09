# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script is use to test PMK Roaming with EAP-WPA2-TKIP or EAP-WPA2-AES
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'target_station':
                        The target station ip address.
                        This station should be an Windows XP SP2 with
                        Broadcom wireless card.
                    'test_mode':
                        l3/l2 (Optional). By default test on L2LWAPP APs
                    'active_ap_list':
                        list of 2 active aps. Request when 'test_mode' is 'l3'
                    'encryption_option':
                        TKIP/AES (Optional). The test run default with AES
   Result type: PASS/FAIL/ERROR
   Results:

   Messages:
       If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Base on test option, we will configure the active ap:
            + Configure the wlan (EAP-WPA2-TKIP or EAP-WPA2-AES) on Zone Director
            + Configurate L3 APs if the test mode is L3. Disable all wlan in non active APs
   2. Test:
       - Associate target station to wlan of ZD system
            + Verify if there is a PMK key be created
            + Verify there is Radius traffic between ZD and server
       - Do the roaming between APs
            + Verify if there is no new PMK key be created
            + Verify there is no Radius traffic between ZD and server
            + The station still ping to server successfully
   3. Cleanup:
       - Return the original configuration

   How it is tested?

"""

import time
import re
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.ZoneDirectorCLI import ZoneDirectorCLI

class ZD_PMK_Cache_Roaming(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector',
                           'LinuxPC', 'NetgearL3Switch']
    test_parameters = {'target_station':
                            'The target station ip address. \
                             This station should be an Windows XP SP2 with \
                             Broadcom wireless card.',
                       'test_mode':
                            'l3/l2 (Optional). By default test on L2LWAPP APs',
                       'active_ap_list':
                            'list of 2 active aps. Request when "test_mode" is "l3"',
                       'encryption_option':
                            'TKIP/AES (Optional). The test run default with AES'}

    def config(self, conf):
        # Define the testing parameters
        self._initTestParamesters(conf)
        # Setting the target station for testing
        self._cfgTargetStation()
        # Setting the Zone Director for testing
        self._cfgZoneDirector()
        # Setting for L3LWAPPS Active APs
        if self.test_mode and self.test_mode.lower() == 'l3':
            self._cfgL3ActiveAPs()


    def test(self):
        self._testRoaming()
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

        if self.active_ap_1:
            self._cfg_apConnectionMode(self.active_ap_1, self.active_ap_1_mac,
                                       self.active_ap_1_cfg['tunnel_mode'], 'l2')

        if self.active_ap_2:
            self._cfg_apConnectionMode(self.active_ap_1, self.active_ap_1_mac,
                                       self.active_ap_1_cfg['tunnel_mode'], 'l2')

        self._verifyIfAllAPConnected()

        # Remove all wlan configuration on target station
        if self.target_station:
            tconfig.remove_all_wlan_from_station(self.target_station)


    def _initTestParamesters(self, conf):
        self.target_station = None
        self.active_ap_1 = None
        self.active_ap_1_mode = None
        self.active_ap_2 = None
        self.active_ap_2_mode = None
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

        self.test_mode = None
        if conf.has_key('test_mode'):
            if conf['test_mode'].lower() in ['l3', 'l2']:
                self.test_mode = conf['test_mode'].lower()

            else:
                raise Exception('Test mode "%s" is invalid' % conf['test_mode'])

        # Define the testing wlan configuration
        ssid = 'PMK Cache Roaming - %s' % time.strftime("%H%M%S")
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
                msg = 'The test support encryption mode "TKIP" or "AES" but "%s"' % \
                      conf['encryption_option']
                logging.info(msg)
                raise Exception(msg)

        else:
            self.wlan_cfg['encryption'] = 'AES'
            self.wlan_cfg['sta_encryption'] = 'AES'

        # Create an ssh session to the Zone Director
        zdconfig = {'ip_addr':self.zd.ip_addr,
                    'username':self.zd.username,
                    'password':self.zd.password}
        self.zdcli = ZoneDirectorCLI(zdconfig)


    def _cfgTargetStation(self):
        self.target_station = tconfig.get_target_station(
                                  self.conf['target_station'],
                                  self.testbed.components['Station'],
                                  check_status_timeout = self.check_status_timeout,
                                  remove_all_wlan = True)

        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

        self.target_station_wifi_ip_addr = None
        self.target_station_wifi_macaddr = None


    def _cfgL3ActiveAPs(self):
        if not self.conf.has_key('active_ap_list'):
            raise Exception('L3LWAPP - PMK Roaming needs 2 active APs for testing')

        if self.conf.has_key('active_ap_list') and len(self.conf['active_ap_list']) == 2:
            ap1 = self.conf['active_ap_list'][0]
            ap2 = self.conf['active_ap_list'][1]
            self.active_ap_1 = tconfig.get_testbed_active_ap(self.testbed, ap1)
            self.active_ap_1_mac = self.testbed.get_ap_mac_addr_by_sym_name(ap1)
            self.active_ap_1_cfg = lib.zd.aps.get_ap_detail_info_by_mac_addr(
                                       self.zd,
                                       self.active_ap_1_mac)

            self._cfg_apConnectionMode(self.active_ap_1, self.active_ap_1_mac,
                                       self.active_ap_1_cfg['tunnel_mode'], 'l3')

            self.active_ap_2 = tconfig.get_testbed_active_ap(self.testbed, ap2)
            self.active_ap_2_mac = self.testbed.get_ap_mac_addr_by_sym_name(ap2)
            self.active_ap_2_cfg = lib.zd.aps.get_ap_detail_info_by_mac_addr(
                                       self.zd,
                                       self.active_ap_2_mac)

            self._cfg_apConnectionMode(self.active_ap_2, self.active_ap_2_mac,
                                       self.active_ap_2_cfg['tunnel_mode'], 'l3')

        self.active_ap_list = [self.active_ap_1, self.active_ap_2]
        self._downAllWlanOnNonActiveAPs()


    def _downAllWlanOnNonActiveAPs(self):
        # Remove the WLAN on the non-active APs and verify the status on the active AP
        for ap in self.testbed.components['AP']:
            if ap not in self.active_ap_list:
                logging.info("Remove all WLAN on non-active AP %s" % ap.get_base_mac())
                ap.remove_all_wlan()


    def _cfg_apConnectionMode(self, ap, ap_mac, current_mode, mode):
        if current_mode.lower() != mode.lower():
            logging.info('Connect Active AP with ZD through %sLWAPP' % mode.upper())
            self.testbed.configure_ap_connection_mode(ap_mac, mode)
            self._verifyActiveAPConnection(ap, ap_mac)
            if self.errmsg:
                raise Exception(self.errmsg)


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

        logging.info("Configure a WLAN with SSID %s on the Zone Director" % \
                     self.wlan_cfg['ssid'])

        self.zd.cfg_wlan(self.wlan_cfg)
        # Wait a moment for ZD to push config to the APs
        time.sleep(2)


    def _verifyActiveAPConnection(self, ap, ap_mac):
        start_time = time.time()
        time_out = time.time() - start_time
        connected = True

        while time_out < self.check_status_timeout:
            time_out = time.time() - start_time
            ap_info = self.zd.get_all_ap_info(ap_mac)
            if ap_info:
                if 'connected' not in ap_info['status'].lower():
                    connected = False
                    time.sleep(30)

                else:
                    connected = True
                    logging.info('Ruckus AP[%s] is connected to Zone Director with IP [%s]'
                                 % (ap_mac, ap_info['ip_addr']))
                    self.errmsg = ''
                    break

            else:
                connected = False
                time.sleep(10)

        if not connected:
            msg = 'AP [%s] does not connect to ZD system after %s seconds'
            self.errmsg = msg % (ap_mac, repr(self.check_status_timeout))

    def _verfiyRoamingEvent(self, ap_mac):
        """
        Verify if there are any roaming event from expected ap
        Input: ap_mac: Mac address of the AP that client will roam from
        """
        all_events = self.zd.get_events()
        logging.info('Get all Events on Zone Director during roaming')

        # MSG_client_roam_in={ap} radio {radioto} detects \
        # {user} in {wlan} roams from {apfrom}
        expected_msg = self.zd.messages['MSG_client_roam_in']
        expected_msg = expected_msg[expected_msg.find('{user}'):]
        expected_msg = expected_msg.replace(
                           '{user}', 'User[%s@%s]' % \
                           (self.wlan_cfg['username'],
                            self.target_station_wifi_macaddr.lower()))
        expected_msg = expected_msg.replace(
                           '{wlan}', 'WLAN[%s]' % self.wlan_cfg['ssid'])
        expected_msg = expected_msg.replace(
                           '{apfrom}', 'AP[%s]' % ap_mac)

        logging.info(expected_msg)
        logging.info(all_events)
        roaming_event = False
        for event in all_events:
            if expected_msg in repr(event):
                roaming_event = True
                logging.info('Roaming successfully: [%s]' % repr(event))
                break

        if not roaming_event:
            raise Exception('The roaming event is not exist')

    def _verifyStationAssociation(self):
        # Access the target station to Zone Director system
        msg = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_cfg,
                                              self.check_status_timeout)
        if msg:
            raise Exception(msg)

        # Verify the if client get the IP address successfully
        val1, val2, val3 = tmethod.renew_wifi_ip_address(self.target_station,
                                                         self.check_status_timeout)
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
                    msg = 'There no PMK key for station %s' % \
                          self.target_station_wifi_macaddr
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


    def _verifyIfRoamingOccur(self):
        # Check if the target station roam to another AP
        current_time = time.time()
        while True:
            roam_ap_mac = None
            time_out = time.time() - current_time
            target_sta_info_on_zd = tmethod.get_active_client_by_mac_addr(
                                        self.target_station_wifi_macaddr,
                                        self.zd)

            if target_sta_info_on_zd:
                if target_sta_info_on_zd['apmac'] != self.joined_ap_mac:
                    roam_ap_mac = target_sta_info_on_zd['apmac']

            if roam_ap_mac or time_out > self.check_status_timeout:
                break

            time.sleep(30)

        if not target_sta_info_on_zd:
            msg = 'There is no information about target station [%s] on Zone Director \
                  after do the roaming'
            msg = msg % self.target_station_wifi_macaddr

            raise Exception(msg)

        if not roam_ap_mac:
            msg = 'The roaming did not happen after %s seconds' % self.check_status_timeout
            raise Exception(msg)

        # Verify if there are any event occur
        self._verfiyRoamingEvent(self.joined_ap_mac)


    def _testRoaming(self):
        # Access target station to Zone director and verify if it access successully
        self._verifyStationAssociation()

        # Verify if there is an entry of target station on Zone Director
        target_sta_info_on_zd = tmethod.get_active_client_by_mac_addr(
                                    self.target_station_wifi_macaddr,
                                    self.zd)

        if not target_sta_info_on_zd:
            msg = 'There is not information about client [%s] on Zone Director' % \
                  self.target_station_wifi_macaddr

            raise Exception(msg)

        # Verify there is an PMK entry for target station
        pmk_count_before_roaming, pmk_info = self._verifyPMKCacheInfo()
        if self.errmsg or not pmk_count_before_roaming:
            return

        self.zd.clear_all_events()
        logging.info('Clear all events on Zone Director')

        # Start sniffer on linux server to verify the radius traffic between
        # Zone Director and Server
        self.linux_server.start_sniffer(self.params_for_sniffer)

        # Restart the AP that client joined to make roaming
        self.joined_ap_mac = target_sta_info_on_zd['apmac']
        self.joined_ap = tconfig.get_testbed_active_ap(self.testbed,
                                                       self.joined_ap_mac)

        if not self.joined_ap:
            raise Exception('Could not find the AP [%s] that station joined' % \
                            target_sta_info_on_zd['apmac'])

        self.joined_ap.reboot()

        # Verify if the roaming happening
        self._verifyIfRoamingOccur()

        # Verify if there is any Radius packet between Zone Director and Server
        self.linux_server.stop_sniffer()
        self._verifyRadiusPacket(False)
        if self.errmsg:
            self.errmsg = 'Roaming successfully but %s' % self.errmsg
            return

        # Verify there is not any new PMK key for target station
        pmk_count_after_roaming, pmk_info = self._verifyPMKCacheInfo()
        if self.errmsg:
            self.errmsg = 'Roaming successfully but %s' % self.errmsg
            return

        if pmk_count_after_roaming != pmk_count_before_roaming:
            msg = 'Roaming successfully but the PMK count is changed \
                  [Before: %s - After: %s]'

            msg = msg % (pmk_count_before_roaming, pmk_count_after_roaming)
            self.errmsg = msg

            return

        # Verify the if target station still ping to server successfully
        msg = tmethod.client_ping_dest_is_allowed(self.target_station,
                                                  self.linux_server.ip_addr,
                                                  self.ping_timeout)
        if msg:
            self.errmsg = 'Roaming successfully but %s' % msg
            return

