# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: IPTV_Dead_Station_Count class tests ability of stopping sending traffic to dead station.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):

    1. Build under test is loaded on the AP
    Required components: RuckusAP, StationLinuxPC
    Test parameters: {'active_ap': 'ip address of active ap',
                      'remote_station': 'ip address of remote linux pc',
                      'local_station': 'ip address of local linux pc',
                      'active_ad': 'ip address of active adapter'}

    Result type: PASS/FAIL

    Results: PASS: Verify that while streaming traffic, and down svcp interface on the adapter, AP does not
                    send traffic out its svcp interface anymore, and the dead station can not receive traffic.
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
        - Streaming traffic from the local station to remote station. Verify that remote station can receive traffic
        correctly
        - Down svcp interface on the active adapter.
        - Verify that local station can not ping to remote station because wireless network is down
        - Verify athstats on the AP to make sure that AP stopped sending traffic out svcp interface
    3. Cleanup:
        - Return the previous QoS configuration for the AP
        - Down svcp interface on the AP and adapter

    How is it tested:
        - While streaming traffic, after downing svcp interface on the adapter, login to adapter CLI and turn on
        svcp interface. The script should return FAIL, and report that AP sends too many packets out svcp interface
        while wireless network is down.
"""

import time
import logging
import tempfile

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
from libIPTV_TestConfig import *
from libIPTV_TestMethods import *

class IPTV_Dead_Station_Count(Test):
    required_components = ['RuckusAP', 'StationLinuxPC']
    parameter_description = {'active_ap': 'ip address of active ap',
                             'remote_station': 'ip address of remote linux pc',
                             'local_station': 'ip address of local linux pc',
                             'active_ad': 'ip address of active adapter'}

    def config(self, conf):

        self.ap_ip_addr = conf['active_ap']
        self.ad_ip_addr = conf['active_ad']

        # Find exactly station
        self.remote_station = None
        self.local_station = None
        self.active_ap = None
        self.ad_config = {}
        self.ap_channel = conf['ap_channel']
        self.wlan_if = conf['wlan_if']
        self.use_pppoe = conf['use_pppoe']
        self.timeout = '60'

        # Find exactly remote station and local station
        station_list = self.testbed.components['Station']
        self.remote_station = getStation(conf['remote_station'], station_list)
        self.local_station = getStation(conf['local_station'], station_list)

        logging.info("Find the active AP object")
        self.active_ap = getTestbedActiveAP(self.testbed, conf['active_ap'],
                                            self.testbed.components['AP'],
                                            self.ap_channel, self.wlan_if)

        logging.info("Get active adapter configuration information")
        self.ad_config = getADConfig(self.testbed, conf['active_ad'], self.testbed.ad_list)

        # Get AP model
        self.model = self.active_ap.get_device_type().lower()
        self.ad_model = self.remote_station.get_ad_device_type(self.ad_config)

        logging.info("Save encryption information")
        self.current_ap_encryption = self.active_ap.get_encryption(self.wlan_if)
        self.current_ap_encryption['wlan_if'] = self.wlan_if
        logging.info("Current ap encryption: %s" % self.current_ap_encryption)

        self.current_ad_encryption = self.remote_station.get_ad_encryption(self.ad_config, 'wlan0')
        self.current_ad_encryption['wlan_if'] = 'wlan0'

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

        logging.info("Turn on svcp interface on the active adapter %s" % self.ad_ip_addr)
        self.remote_station.set_ruckus_ad_state(self.ad_config, 'up', 'wlan0')
        if self.ad_model.lower() == 'vf7111': time.sleep(60)
        else: time.sleep(2)

        self._get_ip_addrs()
        # Verify connection between stations
        verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_sta_ip_addr)

        logging.info("Start iperf server on the station %s" % self.remote_sta_ip_addr)
        self.remote_station.start_iperf(test_udp = True)
        time.sleep(1)

        fo, tcpdump_info_file = tempfile.mkstemp(".txt")
        logging.info("Use tool tcpdump to capture traffic on the remote station %s" % self.remote_sta_ip_addr)
        self.remote_station.start_tcp_dump(ip_addr = self.remote_sta_ip_addr,
                                         proto = "udp", count = "40",
                                         file_path = tcpdump_info_file)

        logging.info("Start iperf client on the station %s" % self.local_sta_ip_addr)
        self.local_station.start_iperf(serv_addr = self.remote_sta_ip_addr, test_udp = True, timeout = "1800")
        time.sleep(30)

        logging.info("Analyze traffic to make sure that station behind the adapter (%s) is receiving traffic" %
                     self.remote_sta_ip_addr)
        cap_traffic_res = self.remote_station.analyze_traffic(tcpdump_info_file)
        capture_ok = False
        for res in cap_traffic_res:
            if res['src_ip'] == self.local_sta_ip_addr and res['dst_ip'] == self.remote_sta_ip_addr:
                capture_ok = True
                break
        if not capture_ok:
            msg = "Can not capture traffic with source ip address %s " % self.local_sta_ip_addr
            msg += " and destination ip address %s while streaming traffic" % self.remote_sta_ip_addr
            raise Exception(msg)
        logging.info("Station %s is receiving traffic from station %s" %
                     (self.remote_sta_ip_addr, self.local_sta_ip_addr))

        logging.info("Down interface svcp on the adapter %s" % self.ad_ip_addr)
        self.remote_station.set_ruckus_ad_state(self.ad_config, 'down', 'wlan0')
        time.sleep(2)

        # Verify ping again
        verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_sta_ip_addr, 10000, False)

        logging.info("Verify athstats to make sure that AP stopped sending traffic out svcp interface")
        tries = 3
        while tries:
            first_tx_packet = self.active_ap.get_ath_stats(self.model)
            time.sleep(2)
            second_tx_packet = self.active_ap.get_ath_stats(self.model)
            delta = second_tx_packet - first_tx_packet
            if delta > 50:
                logging.debug("Number of tx frames: %d" % first_tx_packet)
                logging.debug("Number of tx frames after that 2 seconds: %d" % second_tx_packet)
                break
            tries = tries - 1
            time.sleep(1)
            continue
        if tries:
            return ["FAIL", "AP sends too many packets out svcp interface while wireless network is down"]

        logging.info("AP stopped sending traffic out svcp interface")
        return ["PASS", ""]

    def cleanup(self):

        if self.local_station:
            logging.info("Kill iperf client processes")
            self.local_station.stop_iperf()
        if self.remote_station:
            logging.info("Kill iperf server processes")
            self.remote_station.stop_iperf()
            self.remote_station.set_ruckus_ad_state(self.ad_config, 'down', 'wlan0')
            self.remote_station.cfg_wlan(self.ad_config, self.current_ad_encryption)

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

        if self.active_ap:
            logging.info("Return the previous encryption for AP")
            self.active_ap.cfg_wlan(self.current_ap_encryption)

            logging.info("Down %s interface on the active AP %s" % (self.wlan_if, self.ap_ip_addr))
            self.active_ap.set_state(self.wlan_if, 'down')

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
