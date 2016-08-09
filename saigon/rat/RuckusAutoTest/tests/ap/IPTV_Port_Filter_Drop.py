# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: IPTV_Port_Filter_Drop class tests ability of dropping traffic when streaming traffic
with matching Drop Filter rule.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):

    1. Build under test is loaded on the AP
    Required components: RuckusAP, StationLinuxPC
    Test parameters: {'active_ap': 'ip address of active ap',
                      'remote_station': 'ip address of remote linux pc',
                      'local_station': 'ip address of local linux pc',
                      'active_ad': 'ip address of active adapter'}

    Result type: PASS/FAIL

    Results: PASS: Add a Port Matching Filter rule with drop action, verify that when streaming traffic
                    that matching this rule, traffic will be dropped, and voice/video queues are empty
             FAIL: If one of the above criteria is not safisfied.

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:
        - Look for the active AP, active adapter and local station and remote station in the testbed.
        - Save the current QoS configuration on the active AP
    2. Test:
        - Turn off all wlans on non-active APs
        - Turn on svcp interface on the active AP and active adapter
        - Verify connections between AP and adapter to make sure that adapter associate to the AP successfully
        - Add a Port Matching Filter to the AP with destination port, proto is UDP, and action is Drop
        - Verify that when streaming traffic that matching with this rule, traffic will be dropped. Voice and video
        queues are empty
    3. Cleanup:
        - Return the previous QoS configuration for the AP
        - Down svcp interface on the AP and adapter

    How is it tested:
        - Before streaming traffic with matching voice ToS value, login to AP CLI and change content of filter rule
        from drop action to ToS action for voice. The script should return FAIL, and report that voice queue is not empty.
"""

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
from libIPTV_TestConfig import *
from libIPTV_TestMethods import *

class IPTV_Port_Filter_Drop(Test):
    required_components = ['RuckusAP', 'StationLinuxPC']
    parameter_description = {'active_ap': 'ip address of active ap',
                             'remote_station': 'ip address of remote linux pc',
                             'local_station': 'ip address of local linux pc',
                             'active_ad': 'ip address of active adapter'}

    def config(self, conf):

        self.wlan_if = conf['wlan_if']
        self.use_pppoe = conf['use_pppoe']
        self._defineTestParams(conf)
        self._getStations(conf)

        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        self.ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['active_ad'])

        logging.info("Find the active AP object")
        self.active_ap = getTestbedActiveAP(self.testbed, conf['active_ap'], self.testbed.components['AP'],
                                            self.ap_channel, self.wlan_if)
        self.eth_interface = self.active_ap.get_eth_inferface_name()

        logging.info("Get active adapter configuration information")
        self.ad_config = getADConfig(self.testbed, conf['active_ad'], self.testbed.ad_list)
        self._saveConfig()

    def test(self):
        wlan_cfg = dict(auth="PSK",
                        wpa_ver="WPA",
                        encryption="AES",
                        key_string="AES_12345678",
                        ssid='IPTV',
                        wlan_if='%s' % self.wlan_if)
        logging.info("Configure a WLAN with SSID %s on the active AP" % wlan_cfg['ssid'])
        self.active_ap.cfg_wlan(wlan_cfg)

        ad_wlan_cfg = wlan_cfg.copy()
        ad_wlan_cfg['wlan_if'] = 'wlan0'
        logging.info("Configure a WLAN with SSID %s  on the active adapter" % wlan_cfg['ssid'])
        self.remote_station.cfg_wlan(self.ad_config, ad_wlan_cfg)

        logging.info("Turn on svcp interface on this adapter")
        self.remote_station.set_ruckus_ad_state(self.ad_config, 'up', 'wlan0')
        if self.ad_model.lower() == 'vf7111': time.sleep(60)
        else: time.sleep(2)

        self._get_ip_addrs()
        # Verify connection between stations
        verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_sta_ip_addr)

        # Enable ToS classification on the active AP
        self.active_ap.set_tos_classification(self.eth_interface, True)

        msg = "Add Port Matching Filter to the AP: proto ---> %s, port ---> %s, " % (self.proto, self.port)
        msg += "action ---> %s" % self.action
        logging.info(msg)
        self.active_ap.add_port_matching_rule(self.eth_interface, self.proto, self.action, self.port, self.dest_port)

        logging.info("Start iperf server on the station %s" % self.remote_sta_ip_addr)
        self.remote_station.start_iperf(test_udp = True)

        logging.info("Clear media queue statistics on the active ap")
        self.active_ap.clear_mqstats(self.wlan_if)

        logging.info("Start to stream traffic from the station %s to the remote station %s" %
                     (self.local_sta_ip_addr, self.remote_sta_ip_addr))
        self.local_station.start_iperf(serv_addr = self.remote_sta_ip_addr, test_udp = True,
                                      timeout = self.timeout, bw = self.bw)
        time.sleep(int(self.timeout))

        mq_statistics = getStaMQStatistics(self.active_ap, self.ad_mac, self.wlan_if)
        for each_queue in mq_statistics.keys():
            if each_queue == 'voice' or each_queue == 'video':
                if int(mq_statistics[each_queue]['deq']) > 50:
                    return ["FAIL", "%s queue has %s packets while it must be empty" %
                            (each_queue, mq_statistics[each_queue]['deq'])]

        logging.info("Video and voice queues are empty because all traffic is dropped by Port Matching Filter")
        return ["PASS", ""]

    def cleanup(self):

        if self.active_ap:
            logging.info("Return the previous encryption for AP")
            self.active_ap.cfg_wlan(self.current_ap_encryption)

            logging.info("Return the previous status of ToS classification")
            self.active_ap.set_tos_classification(self.eth_interface, self.cur_tos_classify_status)

            if self.cur_port_match_status:
                logging.info("Return the previous status of Port Match")
                self.active_ap.set_port_match_status(self.cur_port_match_status, self.eth_interface)

            logging.info("Remove port matching filter")
            self.active_ap.remove_port_matching_rule(self.eth_interface)

            logging.info("Down %s interface on the active AP %s" % (self.wlan_if, self.ap_ip_addr))
            self.active_ap.set_state(self.wlan_if, 'down')

        if self.ad_config:
            logging.info("Down svcp interface on the active AD %s" % self.ad_ip_addr)
            self.remote_station.set_ruckus_ad_state(self.ad_config, 'down', 'wlan0')
            self.remote_station.cfg_wlan(self.ad_config, self.current_ad_encryption)

        if self.local_station:
            logging.info("Kill iperf client processes")
            self.local_station.stop_iperf()
        if self.remote_station:
            logging.info("Kill iperf server processes")
            self.remote_station.stop_iperf()

            if self.use_pppoe:
                start_time = time.time()
                while time.time() - start_time < self.timeout:
                    self.remote_sta_ip_addr = getLinuxIpAddr(self.remote_station, self.testbed.sta_pppoe_subnet)
                    if not self.remote_sta_ip_addr:
                        break
                    time.sleep(1)
                if self.remote_sta_ip_addr:
                    raise Exception("IP address of PPP interface still appears after %s seconds downing PPPoE connection" %
                                    self.timeout)
        logging.info("---------- FINISH ----------")

    def _defineTestParams(self, conf):

        # Port matching filter parameters
        self.proto = "udp"
        self.action = "drop"
        self.port = "5001"
        self.dest_port = True

        # Iperf parameters
        self.timeout = "60"
        self.bw = "4m"

        # Find exactly station
        self.remote_station = None
        self.local_station = None
        self.active_ap = None
        self.ad_config = {}
        self.ap_channel = conf['ap_channel']

    def _get_ip_addrs(self):

        # Find the ip address of interface that connected to the adapter on the local station and remote station
        if not self.use_pppoe:
            self.remote_sta_ip_addr = getLinuxIpAddr(self.remote_station, self.testbed.sta_wifi_subnet)
            self.local_sta_ip_addr = getLinuxIpAddr(self.local_station, self.testbed.sta_wifi_subnet)

            if not self.local_sta_ip_addr or not self.remote_sta_ip_addr:
                raise Exception("IP address of interface that connecting to the adapter is not correct")
        else:
            self.local_sta_ip_addr = getLinuxIpAddr(self.local_station, self.testbed.sta_pppoe_subnet)
            if not self.local_sta_ip_addr:
                raise Exception("IP address of interface that connecting to the AP is not correct")

            start_time = time.time()
            while time.time() - start_time < self.timeout:
                self.remote_sta_ip_addr = getLinuxIpAddr(self.remote_station, self.testbed.sta_pppoe_subnet)
                if self.remote_sta_ip_addr:
                    break
                time.sleep(1)
            if not self.remote_sta_ip_addr:
                raise Exception("PPP connection is not up after %s seconds" % self.timeout)

    def _getStations(self, conf):
        # Find exactly stations
        station_list = self.testbed.components['Station']
        self.remote_station = getStation(conf['remote_station'], station_list)
        self.local_station = getStation(conf['local_station'], station_list)

    def _saveConfig(self):
        logging.info("Save encryption information")
        self.current_ap_encryption = self.active_ap.get_encryption(self.wlan_if)
        self.current_ap_encryption['wlan_if'] = self.wlan_if

        self.current_ad_encryption = self.remote_station.get_ad_encryption(self.ad_config, 'wlan0')
        self.current_ad_encryption['wlan_if'] = 'wlan0'

        logging.info("Save current QoS configuration on the active AP")
        self.cur_tos_classify_status = self.active_ap.get_tos_classification(self.eth_interface)
        self.cur_port_match_status = saveCurPortMatchingFilterStatus(self.active_ap, self.eth_interface)
        self.ad_mac = self.remote_station.get_ad_wireless_mac(self.ad_config)
        self.ad_model = self.remote_station.get_ad_device_type(self.ad_config)
