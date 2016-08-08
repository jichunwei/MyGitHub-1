# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: IPTV_Streaming_Combination class tests ability of queuing traffic when streaming with the given conditions.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):
    1. Build under test is loaded on the AP

    Required components: RuckusAP, StationLinuxPC
    Test parameters:{'active_ap': 'ip address of active ap',
                             'remote_station': 'ip address of remote linux pc',
                             'local_station': 'ip address of local linux pc',
                             'active_ad': 'ip address of active adapter',
                             'passive_ad': 'ip address of passive adapter',
                             'igmp_snooping':'decide if IGMP Snooping is enabled or not',
                             'directed_mcast':'decide if Directed Mcast is enabled or not',
                             'directed_bcast':'decide if Directed Bcast is enabled or not',
                             'queue':'name of queue that traffic will be inserted to',
                             'tos_matching':'decide of traffic is matching with ToS value or not',
                             'tos_classify_value':'value of ToS',
                             'media':'name of a kind of media, e.g voice, video, data, background',
                             'stream_with_multi_sta':'decide if streaming traffic to multi stations',
                             'verify_bcast_threshold':'decide if Bcast Threshold is tested or not'
    }

    Result type: PASS/FAIL/N/A

    Results: PASS: if all the above criteria are satisfied.
             FAIL: If one of the above criteria is not satisfied.
             N/A: If the test procedure need to run on specific customer ID

    Messages: If FAIL the test script returns a message related to the criterion that is not satisfied.

    Test procedure:
    1. Config:
        - Look for the active AP, active adapter and local station and remote station in the testbed.
        - Save the current QoS configuration on the active AP
    2. Test:
        - Turn off all wlans on non-active APs
        - Turn on svcp interface on the active AP and active adapter
        - Verify connections between AP and adapter to make sure that adapter associate to the AP successfully
        - Change QoS configuration option on the AP with information get from test parameters.
        - Verify traffic put to appropriate media queue and station received correct traffic.

    3. Cleanup:
        - Return the previous QoS configuration for the AP
        - Down svcp interface on the AP and adapter
"""

import time
import logging
import tempfile

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
from libIPTV_TestConfig import *
from libIPTV_TestMethods import *

class IPTV_Multicast_Combination(Test):
    required_components = ['RuckusAP', 'StationLinuxPC']
    parameter_description = {'active_ap': 'ip address of active ap',
                             'remote_station': 'ip address of remote linux pc',
                             'local_station': 'ip address of local linux pc',
                             'active_ad': 'ip address of active adapter',
                             'passive_ad': 'ip address of passive adapter',
                             'igmp_snooping':'decide if IGMP Snooping is enabled or not',
                             'directed_mcast':'decide if Directed Mcast is enabled or not',
                             'directed_bcast':'decide if Directed Bcast is enabled or not',
                             'queue':'name of queue that traffic will be inserted to',
                             'tos_matching':'decide of traffic is matching with ToS value or not',
                             'tos_classify_value':'value of ToS',
                             'media':'name of a kind of media, e.g voice, video, data, background',
                             'stream_with_multi_sta':'decide if streaming traffic to multi stations',
                             'verify_bcast_threshold':'decide if Bcast Threshold is tested or not'
    }

    def config(self, conf):
        self._defineTestParams(conf)
        self._getStations(conf)
        self._get_ip_addrs(conf)
        self._addMcastRoute()

        logging.info("Find the active AP object")
        self.active_ap = getTestbedActiveAP(self.testbed,
                                            conf['active_ap'],
                                            self.testbed.components['AP'],
                                            self.ap_channel, self.wlan_if)

        self._getADConfiguration(conf)
        self.eth_interface = self.active_ap.get_eth_inferface_name()
        self.ap_phymode = self.active_ap.get_phy_mode(self.wlan_if)
        self._saveConfig()

    def test(self):
        # Change configuration on wlan interface
        self.capture_station.cfg_wlan_if(ip_addr = self.wireless_interface_ip_addr, channel = self.ap_channel)

        wlan_cfg = dict(auth="open",
                        encryption="none",
                        ssid='IPTV',
                        wlan_if='%s' % self.wlan_if)
        logging.info("Configure a WLAN with SSID %s on the active AP" % wlan_cfg['ssid'])
        self.active_ap.cfg_wlan(wlan_cfg)

        ad_wlan_cfg = wlan_cfg.copy()
        ad_wlan_cfg['wlan_if'] = 'wlan0'
        logging.info("Configure a WLAN with SSID %s on the active adapter" % wlan_cfg['ssid'])
        self.remote_linux_sta.cfg_wlan(self.active_ad_config, ad_wlan_cfg)

        logging.info("Configure a WLAN with SSID %s on the passive adapter" % wlan_cfg['ssid'])
        self.remote_win_sta.cfg_wlan(self.passive_ad_config, ad_wlan_cfg)

        logging.info("Turn on svcp interface on this adapter")
        self.remote_linux_sta.set_ruckus_ad_state(self.active_ad_config, 'up', 'wlan0')
        self.remote_win_sta.set_ruckus_ad_state(self.passive_ad_config, 'up', 'wlan0')
        if self.ad_model.lower() == 'vf7111': time.sleep(60)
        else: time.sleep(2)

        # Verify connection between stations
        verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_linux_sta_ip_addr)
        verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_win_sta_ip_addr)

        # Get BSSID to support capturing packets over the air
        self.bssid = getBSSID(self.active_ap, self.wlan_if)

        if not self.verify_bcast_threshold:
            self.active_ap.set_tos_classification(self.eth_interface, True)
            if self.tos_matching:
                logging.info("Configure ToS classify value (%s) for %s queue" % (self.tos_classify_value, self.media))
                self.active_ap.set_tos_values(self.media, self.tos_classify_value)

            logging.info("%s igmp snooping" % {True:"Enable", False:"Disable"}[self.igmp_snooping])
            self.active_ap.set_igmp_snooping(self.wlan_if, enabled = self.igmp_snooping)

            logging.info("%s directed multicast" % {True:"Enable", False:"Disable"}[self.directed_mcast])
            self.active_ap.set_qos_cfg_option(self.eth_interface, option='directed multicast', enabled = self.directed_mcast)

            logging.info("%s directed broadcast" % {True:"Enable", False:"Disable"}[self.directed_bcast])
            if self.directed_bcast:
                status = 'enable'
                threshold = '30'
            else:
                status = 'disable'
                threshold = '0'
            if not self.build_stream:
                self.active_ap.set_directed_bcast_status(self.wlan_if, status)
            else:
                self.active_ap.set_directed_threshold(self.wlan_if, threshold)
        else:
            if not self.build_stream:
                self.active_ap.set_qos_threshold('DirectedThreshold', self.bcast_threshold)
            else: self.active_ap.set_directed_threshold(self.wlan_if, self.bcast_threshold)

        res, msg = self._streamTraffic()
        if res == "FAIL": return [res, msg]

        return ["PASS", ""]

    def cleanup(self):
        if self.remote_linux_sta and self.local_station and self.remote_win_sta:
            if not self.verify_bcast_threshold:
                logging.info("Kill iperf server process on the remote station %s" % self.remote_linux_sta_ip_addr)
                self.remote_linux_sta.stop_iperf()

            self.remote_linux_sta.cfg_wlan(self.active_ad_config, self.current_active_ad_encryption)
            logging.info("Down svcp interface on the active Adapter")
            self.remote_linux_sta.set_ruckus_ad_state(self.active_ad_config, 'down', 'wlan0')

            self.remote_win_sta.cfg_wlan(self.passive_ad_config, self.current_passive_ad_encryption)
            logging.info("Down svcp interface on the passive Adapter")
            self.remote_win_sta.set_ruckus_ad_state(self.passive_ad_config, 'down', 'wlan0')

            verifyStaConnection(self.local_station,
                                self.local_sta_ip_addr,
                                self.remote_linux_sta_ip_addr,
                                5000, False)
            verifyStaConnection(self.local_station,
                                self.local_sta_ip_addr,
                                self.remote_win_sta_ip_addr,
                                5000, False)

        if self.active_ap:
            if not self.verify_bcast_threshold:
                logging.info("Return the previous status of ToS classification")
                self.active_ap.set_tos_classification(self.eth_interface, self.cur_tos_classify_status)

                if self.tos_matching:
                    logging.info("Return the previous ToS value for %s" % self.media)
                    self.active_ap.set_tos_values(self.media, self.cur_tos_classify_value)

                self.active_ap.set_igmp_snooping(self.wlan_if, enabled = self.cur_igmp_snooping_status)
                self.active_ap.set_qos_cfg_option(self.eth_interface,
                                               option = 'directed multicast',
                                               enabled = self.cur_directed_mcast_status)

            if not self.build_stream:
                self.active_ap.set_directed_bcast_status(self.wlan_if, self.cur_directed_bcast)
            else:
                self.active_ap.set_directed_threshold(self.wlan_if, self.cur_directed_bcast)

            logging.info("Down %s interface on the active AP" % self.wlan_if)
            self.active_ap.set_state(self.wlan_if, 'down')
            time.sleep(2)

        self._delMcastRoute()
        logging.info("---------- FINISH ----------")

    def _saveConfig(self):

        logging.info("Save encryption information")
        self.current_ap_encryption = self.active_ap.get_encryption(self.wlan_if)
        self.current_ap_encryption['wlan_if'] = self.wlan_if

        self.current_active_ad_encryption = self.remote_linux_sta.get_ad_encryption(self.active_ad_config, 'wlan0')
        self.current_active_ad_encryption['wlan_if'] = 'wlan0'

        self.current_passive_ad_encryption = self.remote_win_sta.get_ad_encryption(self.passive_ad_config, 'wlan0')
        self.current_passive_ad_encryption['wlan_if'] = 'wlan0'

        if not self.verify_bcast_threshold:
            logging.info("Save current QoS configuration on the active AP")
            self.cur_tos_classify_status = self.active_ap.get_tos_classification(self.eth_interface)
            if self.tos_matching:
                self.cur_tos_classify_value = saveToSValues(self.active_ap, self.media)

            self.cur_igmp_snooping_status = self.active_ap.get_igmp_snooping(self.wlan_if)
            self.cur_directed_mcast_status = self.active_ap.get_qos_cfg_option()['directed_multicast']

        if not self.build_stream:
            self.cur_directed_bcast = self.active_ap.get_directed_bcast_status(self.wlan_if)
        else:
            self.cur_directed_bcast = self.active_ap.get_directed_threshold(self.wlan_if)

    def _getADConfiguration(self, conf):

        # Get adapter configuration information
        self.active_ad_config = getADConfig(self.testbed, conf['active_ad'], self.testbed.ad_list)
        self.passive_ad_config = getADConfig(self.testbed, conf['passive_ad'], self.testbed.ad_list, "Passive AD")
        self.active_ad_mac = self.remote_linux_sta.get_ad_wireless_mac(self.active_ad_config)
        self.passive_ad_mac = self.remote_win_sta.get_ad_wireless_mac(self.passive_ad_config)
        self.ad_model = self.remote_linux_sta.get_ad_device_type(self.active_ad_config)

    def _getStations(self, conf):
        # Find exactly stations
        station_list = self.testbed.components['Station']
        self.remote_win_sta = getStation(conf['remote_win_sta'], station_list)
        self.remote_linux_sta = getStation(conf['remote_linux_sta'], station_list)
        self.local_station = getStation(conf['local_station'], station_list)
        self.capture_station = getStation(conf['capture_station'], station_list)

    def _get_ip_addrs(self, conf):

        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        self.active_ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['active_ad'])
        self.passive_ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['passive_ad'])

        # Find the ip address of interface that connected to the adapter on the local station and remote station
        self.local_sta_ip_addr, self.local_if_name = getLinuxIpAddr(self.local_station, self.testbed.sta_wifi_subnet, True)
        self.remote_linux_sta_ip_addr, self.remote_linux_if_name = getLinuxIpAddr(self.remote_linux_sta,
                                                                                 self.testbed.sta_wifi_subnet, True)
        self.remote_win_sta_ip_addr, self.remote_win_if_name = getWinsIpAddr(self.remote_win_sta,
                                                                            self.testbed.sta_wifi_subnet, True)
        if not self.local_sta_ip_addr or not self.remote_linux_sta_ip_addr or not self.remote_win_sta_ip_addr:
            raise Exception("Can not find any ip address belongs to subnet %s" % self.testbed.sta_wifi_subnet['network'])

        self.wireless_interface_ip_addr = getLinuxIpAddr(self.capture_station, self.testbed.sta_wireless_interface_info)
        if not self.wireless_interface_ip_addr:
            raise Exception("IP address of wireless interface on the linux station %s is not correct" %
                            conf['capture_station'])

    def _defineTestParams(self, conf):
        # Iperf parameters
        self.timeout = "60"
        self.bw_list = ['4m']

        # tcpdump parameters:
        self.count = "40"
        self.proto = "udp"
        self.windump_info_file = ""
        self.tcpdump_info_file = ""

        # multicast route setting
        self.multicast_network = "224.0.0.0"
        self.multicast_mask = "240.0.0.0"
        self.multicast_group = conf['multicast_group']

        self.ap_channel = conf['ap_channel']
        self.wlan_if = conf['wlan_if']
        self.build_stream = conf['build_stream']

        self.remote_linux_sta = None
        self.remote_win_sta = None
        self.local_station = None
        self.active_ap = None
        self.active_ad_config = {}
        self.passive_ad_config = {} # Adapter used when verifying traffic sent to all stations

        if conf.has_key('media'): self.media = conf['media']
        else: self.media = ""
        if conf.has_key('queue'): self.queue = conf['queue']
        else: self.queue = ""
        if conf.has_key('tos_classify_value'): self.tos_classify_value = conf['tos_classify_value']
        else: self.tos_classify_value = ""
        if conf.has_key('tos_matching'): self.tos_matching = conf['tos_matching']
        else: self.tos_matching = False

        if conf.has_key('verify_bcast_threshold'):
            self.verify_bcast_threshold = conf['verify_bcast_threshold']
            self.bcast_threshold = conf['bcast_threshold']
            self.ipsrc_bcast = conf['ipsrc_bcast']
            self.ipdst_bcast = conf['ipdst_bcast']
            self.packet_replay_file = conf['packet_replay_file']
        else:
            self.verify_bcast_threshold = False
            self.directed_mcast = conf['directed_mcast']
            self.igmp_snooping = conf['igmp_snooping']
            self.directed_bcast = conf['directed_bcast']

    def _addMcastRoute(self):
        # Add route for multicast traffic
        self.local_station.set_route("add",
                                    self.multicast_network,
                                    self.multicast_mask,
                                    self.local_if_name)
        self.remote_linux_sta.set_route("add",
                                       self.multicast_network,
                                       self.multicast_mask,
                                       self.remote_linux_if_name)

    def _delMcastRoute(self):
        logging.info("Delete multicast IP address in route table of local and remote station")
        if self.local_station:
            self.local_station.set_route("del",
                                        self.multicast_network,
                                        self.multicast_mask,
                                        self.local_if_name)
        if self.remote_linux_sta:
            self.remote_linux_sta.set_route("del",
                                           self.multicast_network,
                                           self.multicast_mask,
                                           self.remote_linux_if_name)

    def _streamTraffic(self):

        if self.verify_bcast_threshold:
            # Capture traffic over the air
            fd, tshark_info_file = tempfile.mkstemp(".txt")
            logging.info("Use tshark to capture traffic over the air")
            self.capture_station.capture_traffic_ota(ip_addr = self.wireless_interface_ip_addr,
                                                   filename = tshark_info_file,
                                                   expression = "ether host",
                                                   host = self.bssid,
                                                   count = "500")

            # using tcpreplay to send broadcast packets
            self.local_station.start_tcp_replay(if_name = self.local_if_name,
                                              file_name = self.packet_replay_file,
                                              rate = "0.3")
            time.sleep(10)

            msg = "Verify the case AP does not convert broadcast packets to unicast"
            msg += " because number of associating stations is lager than directed threshold"
            logging.info(msg)
            res, msg = analyzeTrafficOTA(tshark_info_file, self.capture_station, self.ipsrc_bcast,
                                         self.ipdst_bcast, "", False, self.ad_model, self.ap_phymode)
            if res == "FAIL": return [res, msg]
            return ["PASS", ""]

        for bw in self.bw_list:
            logging.info("Stream traffic with bandwidth %sbps" % bw.upper())
            logging.info("Start iperf server on the station %s" % self.remote_linux_sta_ip_addr)
            self.remote_linux_sta.start_iperf(serv_addr = self.multicast_group, test_udp = True, multicast_srv = True)

            # Capture traffic on the remote stations
            self._start_windump(self.multicast_group)
            self._startTcpdump()

            # Verify IGMP table
            found_igmp_entry = get_igmp_table(self.active_ap, self.multicast_group)
            if not self.igmp_snooping:
                if found_igmp_entry:
                    return ["FAIL", "%s entry is added to the IGMP table while igmp snooping is disabled" %
                            self.multicast_group]
                logging.info("Entry %s is not found in IGMP table because igmp snooping is disabled" %
                             self.multicast_group)
            else:
                if not found_igmp_entry:
                    return ["FAIL","%s entry wasn't added to IGMP table" % self.multicast_group]
                logging.info("Found %s entry in IGMP table" % self.multicast_group)

            logging.info("Clear media queue statistics on the active ap")
            self.active_ap.clear_mqstats(self.wlan_if)
            time.sleep(1)

            logging.info("Start multicast streaming from local station[%s] to [%s]" %
                         (self.local_sta_ip_addr, self.multicast_group))
            self.local_station.start_iperf(serv_addr = self.multicast_group , test_udp = True,
                                          timeout = self.timeout, bw = bw, tos = self.tos_classify_value)
            time.sleep(10)

            # Capture traffic over the air
            if self.ad_model.lower() != 'vf7111':
                fd, tshark_info_file = tempfile.mkstemp(".txt")
                logging.info("Use tshark to capture traffic over the air")
                self.capture_station.capture_traffic_ota(ip_addr = self.wireless_interface_ip_addr,
                                                       filename = tshark_info_file,
                                                       expression = "ether host",
                                                       host = self.bssid, count = "500")
            time.sleep(int(self.timeout) - 5)

            # Get mq statistics on the linux station
            active_ad_mq_stat = getStaMQStatistics(self.active_ap, self.active_ad_mac, self.wlan_if)
            passive_ad_mq_stat = getStaMQStatistics(self.active_ap, self.passive_ad_mac, self.wlan_if)

            if self.igmp_snooping:
                if self.directed_mcast:
                    if not self.directed_bcast:
                        res, msg = self._verifyMQStats(True, active_ad_mq_stat)
                        if res == "FAIL": return [res, msg]

                        # Analyze traffic over the air
                        if self.ad_model.lower() != 'vf7111':
                            res, msg = analyzeTrafficOTA(tshark_info_file, self.capture_station, self.local_sta_ip_addr,
                                              self.multicast_group, self.queue)
                            if res == "FAIL": return [res, msg]

                        logging.info("Verify that only joining station %s receives traffic" % self.remote_linux_sta_ip_addr)
                        self.remote_win_sta.stop_windump()
                        win_cap_res, linux_cap_res = self._getCapturedPacket(self.multicast_group)
                        if win_cap_res:
                            return ["FAIL", "Station %s can receive traffic while it does not join the group %s" %
                                    (self.remote_win_sta_ip_addr, self.multicast_group)]
                        logging.info("Station %s can not receive traffic" % self.remote_win_sta_ip_addr)
                        if not linux_cap_res:
                            return ["FAIL", "Station %s does not receive traffic while it's joining the group" %
                                    (self.remote_linux_sta_ip_addr, self.multicast_group)]
                        logging.info("Station %s receives traffic correctly" % self.remote_linux_sta_ip_addr)
                else:
                    # Verify 1Mbps case
                    if not self.directed_bcast:
                        if self.ad_model.lower() != 'vf7111':
                            logging.info("Verify the case AP does not convert multicast packets to unicast ones")
                            res, msg = analyzeTrafficOTA(tshark_info_file, self.capture_station, self.local_sta_ip_addr,
                                                         self.multicast_group, "", False, self.ad_model, self.ap_phymode)
                            if res == "FAIL": return [res, msg]
                        res, msg = self._noStaReceiveTraffic(active_ad_mq_stat, passive_ad_mq_stat)
                        if res == "FAIL": return [res, msg]
            else:
                if self.directed_mcast:
                    # No stations can receive traffic
                    if not self.directed_bcast:
                        res, msg = self._noStaReceiveTraffic(active_ad_mq_stat, passive_ad_mq_stat)
                        if res == "FAIL": return [res, msg]
                else:
                    if self.directed_bcast:
                        logging.info("Verify that all stations can receive traffic")
                        self.remote_win_sta.stop_windump()
                        win_cap_res, linux_cap_res = self._getCapturedPacket(self.multicast_group)
                        if not win_cap_res:
                            return ["FAIL", "Station %s does not receive traffic in case directed multicast is disabled" %
                                    self.remote_win_sta_ip_addr]
                        if not linux_cap_res:
                            return ["FAIL", "Station %s does not receive traffic in case directed multicast is disabled" %
                                    self.remote_linux_sta_ip_addr]
                        logging.info("All stations can receive traffic because directed multicast is disabled")
                    else:
                        # Verify 1Mbps case
                        if self.ad_model.lower() != 'vf7111':
                            logging.info("Verify the case AP does not convert multicast packets to unicast ones")
                            res, msg = analyzeTrafficOTA(tshark_info_file, self.capture_station, self.local_sta_ip_addr,
                                                         self.multicast_group, "", False, self.ad_model, self.ap_phymode)
                            if res == "FAIL": return [res, msg]

                        res, msg = self._noStaReceiveTraffic(active_ad_mq_stat, passive_ad_mq_stat)
                        if res == "FAIL": return [res, msg]

        return ["PASS", ""]

    def _start_windump(self, host):
        logging.info("Use tool windump to capture traffic on the windows station %s" % self.remote_win_sta_ip_addr)
        self.windump_info_file = "windump_capture.dmp"
        self.remote_win_sta.start_windump_for_ap(ip_addr = self.remote_win_sta_ip_addr,
                                                 proto = "", count = "30",
                                                 file_path = self.windump_info_file, host = host)

    def _startTcpdump(self):
        logging.info("Use tool tcpdump to capture traffic on the remote station %s" % self.remote_linux_sta_ip_addr)
        fo, self.tcpdump_info_file = tempfile.mkstemp(".txt")
        self.remote_linux_sta.start_tcp_dump(ip_addr = self.remote_linux_sta_ip_addr,
                                             proto = self.proto,
                                             count = self.count,
                                             file_path = self.tcpdump_info_file)

    def _noStaReceiveTraffic(self, active_ad_mq_stat, passive_ad_mq_stat):
        logging.info("Verify that queues of stations are empty")
        res, msg = verifyEmptyQueue(active_ad_mq_stat, self.active_ad_mac)
        if res == "FAIL": return [res, msg]

        res, msg = verifyEmptyQueue(passive_ad_mq_stat, self.passive_ad_mac)
        if res == "FAIL": return [res, msg]
        return ["PASS", ""]

    def _verifyMQStats(self, linux_sta = False, active_ad_mq_stat = {}, windows_sta = False, passive_ad_mq_stat = {}):
        if linux_sta:
            right_queue, empty_queues, empty_deq = get_mqstatsInfo(active_ad_mq_stat, self.queue)
            logging.info("Station %s: Verify that traffic will be inserted to the %s queue" %
                         (self.active_ad_mac, self.queue))
            res, msg = verifyMQStats(self.queue, right_queue, empty_queues,
                                     empty_deq, self.timeout, self.active_ad_mac)
            if res == "FAIL":
                return [res, msg]

        if windows_sta:
            right_queue, empty_queues, empty_deq = get_mqstatsInfo(passive_ad_mq_stat, self.queue)
            logging.info("Station %s: Verify that traffic will be inserted to the %s queue" %
                         (self.passive_ad_mac, self.queue))
            res, msg = verifyMQStats(self.queue, right_queue, empty_queues,
                                     empty_deq, self.timeout, self.passive_ad_mac)
            if res == "FAIL":
                return [res, msg]
        return ["PASS", ""]

    def _getCapturedPacket(self, dst_ip_addr, src_ip_addr = ""):
        if src_ip_addr: src_temp = src_ip_addr
        else: src_temp = self.local_sta_ip_addr

        win_cap_res = findCapturedPacket(self.remote_win_sta,
                                         self.windump_info_file,
                                         src_temp, dst_ip_addr)
        linux_cap_res = findCapturedPacket(self.remote_linux_sta,
                                           self.tcpdump_info_file,
                                           src_temp, dst_ip_addr)
        return win_cap_res, linux_cap_res
