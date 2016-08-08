# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: IPTV_Multicast_Streaming class tests ability of queuing traffic when streaming with the given conditions.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):
    1. Build under test is loaded on the AP

    Required components: RuckusAP, StationLinuxPC
    Test parameters: {'active_ap': 'ip address of active ap',
                             'remote_station': 'ip address of remote linux pc',
                             'local_station': 'ip address of local linux pc',
                             'active_ad': 'ip address of active adapter',
                             'tos_classify_enable':'used to decide if ToS Classification is enabled or not',
                             'queue':'name of media queue',
                             'media':'a kind of media, e.g voice, or video, or data, or background',
                             'tos_matching':'used to decide if streamed traffic is matching with ToS or not',
                             'tos_classify_value':'the ToS value that traffic uses',
                             'port_matching_filter':'decide if Port Matching Filter is configured or not',
                             'directed_multicast':'decide if Directed Multicast is enabled or not',
                             'igmp_snooping':'decide if IGMP Snooping is enabled or not',
                             'heuristics_enable':'decide if Heuristics is enabled or not'
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
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
from libIPTV_TestConfig import *
from libIPTV_TestMethods import *

class IPTV_Multicast_Streaming(Test):
    required_components = ['RuckusAP', 'StationLinuxPC']
    parameter_description = {'active_ap': 'ip address of active ap',
                             'remote_station': 'ip address of remote linux pc',
                             'local_station': 'ip address of local linux pc',
                             'active_ad': 'ip address of active adapter',
                             'tos_classify_enable':'used to decide if ToS Classification is enabled or not',
                             'queue':'name of media queue',
                             'media':'a kind of media, e.g voice, or video, or data, or background',
                             'tos_matching':'used to decide if streamed traffic is matching with ToS or not',
                             'tos_classify_value':'the ToS value that traffic uses',
                             'port_matching_filter':'decide if Port Matching Filter is configured or not',
                             'directed_multicast':'decide if Directed Multicast is enabled or not',
                             'igmp_snooping':'decide if IGMP Snooping is enabled or not',
                             'heuristics_enable':'decide if Heuristics is enabled or not'
                             }

    def config(self, conf):
        logging.info('Test config: %s' % pformat(conf))
        self._getQoSTestParams(conf)
        self._defineTestParams(conf)
        self._getStations(conf)
        self._get_ip_addrs(conf)

        self._addMcastRoute()
        if self.stream_with_multi_sta:
            self.remote_win_sta.add_route(self.multicast_network, self.multicast_mask, self.remote_win_sta_ip_addr)

        logging.info("Find the active AP object")
        self.active_ap = getTestbedActiveAP(self.testbed,
                                            conf['active_ap'],
                                            self.testbed.components['AP'],
                                            self.ap_channel, self.wlan_if)
        self.eth_interface = self.active_ap.get_eth_inferface_name()

        self._getADConfiguration(conf)
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
        logging.info("Configure a WLAN with SSID %s  on the active adapter" % wlan_cfg['ssid'])
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

        logging.info("%s ToS Classification" % {True:"Enable", False:"Disable"}[self.tos_classify_enable])
        self.active_ap.set_tos_classification(self.eth_interface, self.tos_classify_enable)

        if not self.heuristics_enable:
            heuristiscs_status = {True:"Enable", False:"Disable"}[self.heuristics_enable]
            logging.info("%s Heuristics" % heuristiscs_status)
            self.active_ap.set_heuristics_status(heuristiscs_status.lower(), self.eth_interface)

        # If streamed traffic has ToS value that is the same as the one configured in any media queue
        if self.tos_matching:
            logging.info("Configure ToS classify value (%s) for %s queue" % (self.tos_classify_value, self.media))
            self.active_ap.set_tos_values(self.media, self.tos_classify_value)

        # If Port Matching Filter is added
        if self.port_matching_filter:
            msg = "Add Port Matching Filter to the AP: proto ---> %s, port ---> %s, " % (self.proto, self.port)
            msg += "action ---> %s" % self.action
            logging.info(msg)
            self.active_ap.add_port_matching_rule(self.eth_interface, self.proto, self.action,
                                               self.port, self.dest_port, self.media)

        if self.test_directed_multicast:
            logging.info("%s directed multicast" % {True:"Enable", False:"Disable"}[self.directed_multicast])
            self.active_ap.set_qos_cfg_option(self.eth_interface,
                                           option='directed multicast',
                                           enabled = self.directed_multicast)

        if self.test_unknown_multicast_drop:
            logging.info("%s unknown multicast drop" % {True:"Enable", False:"Disable"}[self.unknown_multicast_drop])
            self.active_ap.set_qos_cfg_option(self.eth_interface,
                                           option='unknown_mcast',
                                           enabled = self.unknown_multicast_drop)

        if self.test_igmp_snooping:
            logging.info("%s igmp snooping" % {True:"Enable", False:"Disable"}[self.igmp_snooping])
            self.active_ap.set_igmp_snooping(self.wlan_if, enabled = self.igmp_snooping)

        # If script is used to test maximum igmp groups or test IGMPv3
        if self.max_igmp_group or self.igmp_version:
            cur_igmp_table = self.active_ap.get_igmp_table()
            if cur_igmp_table:
                logging.info("Reboot AP to clear the current IGMP table")
                self.active_ap.reboot()
                time.sleep(5)
                self.active_ap.login() # re-login after reboot

            logging.info("Use tcpreplay to simulate sending maximum igmp groups to network")
            self.remote_linux_sta.start_tcp_replay(if_name = self.remote_linux_if_name,
                                                 file_name = self.packet_replay_file)
            time.sleep(10)
            cur_igmp_table = self.active_ap.get_igmp_table()
            logging.info("Current IGMP table: %s" % cur_igmp_table)

            if self.max_igmp_group:
                logging.info("Total IGMP entry: %d" % len(cur_igmp_table))
                if len(cur_igmp_table) < self.max_igmp_group:
                    return ["FAIL", "Can not add maximum (%s) igmp group" % self.max_igmp_group]
                else:
                    return ["PASS", ""]
            if self.igmp_version:
                # verify AP accept IGMPv3 packet
                logging.info("Verify IGMPv3 group in IGMP table")
                for igmp_group in cur_igmp_table:
                    if int(igmp_group.split()[2]) != self.igmp_version:
                        return ["FAIL", "There is an igmp group in IGMP table having incorrect version"]
                return ["PASS", ""]

        # If script is used to test well-known multicast
        if self.test_well_known_multicast:
            logging.info("%s well known multicast forward" %
                         {True:"Enable", False:"Disable"}[self.well_known_multicast])
            self.active_ap.set_qos_cfg_option(self.eth_interface,
                                           option='known_multicast',
                                           enabled = self.well_known_multicast)

            # Capture traffic on the stations
            self._startTcpdump()
            self._start_windump(self.multicast_address_dst)

            # using tcpreplay to send captured wellknown multicast packets
            self.local_station.start_tcp_replay(if_name = self.local_if_name,
                                              file_name = self.packet_replay_file,
                                              rate = "0.1")

            time.sleep(10) # wait for AP sending packets to all STAs
            self.remote_win_sta.stop_windump()
            self.remote_linux_sta.stop_tcp_dump()
            win_cap_res, linux_cap_res = self._getCapturedPacket(self.multicast_address_dst,
                                                                 self.multicast_address_src)
            if not linux_cap_res or not win_cap_res:
                return ["FAIL", "Well-known multicast packets wasn't forwarded to station"]
            else:
                return ["PASS", ""]

        res, msg = self._streamMulticastTraffic()
        return [res, msg]

    def cleanup(self):

        if self.remote_linux_sta and self.local_station and self.remote_win_sta:
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

            if self.stream_with_multi_sta:
                logging.info("Kill iperf server process on the station %s" % self.remote_win_sta_ip_addr)
                self.remote_win_sta.stop_iperf()
                self.remote_win_sta.delete_route(self.multicast_network)

        if self.active_ap:
            logging.info("Return the previous encryption for AP")
            self.active_ap.cfg_wlan(self.current_ap_encryption)

            logging.info("Return the previous status of ToS classification")
            self.active_ap.set_tos_classification(self.eth_interface, self.cur_tos_classify_status)

            if self.tos_matching:
                logging.info("Return the previous ToS value for %s" % self.media)
                self.active_ap.set_tos_values(self.media, self.cur_tos_classify_value)

            if self.port_matching_filter:
                logging.info("Remove all port match filters on the active AP")
                self.active_ap.remove_port_matching_rule(self.eth_interface)

            if self.test_directed_multicast:
                self.active_ap.set_qos_cfg_option(self.eth_interface,
                                               option='directed multicast',
                                               enabled = self.cur_directed_mcast_status)

            if self.test_unknown_multicast_drop:
                self.active_ap.set_qos_cfg_option(self.eth_interface,
                                               option='unknown_mcast',
                                               enabled = self.cur_unknown_mcast_drop_status)

            if self.test_well_known_multicast:
                self.active_ap.set_qos_cfg_option(self.eth_interface,
                                               option='known_multicast',
                                               enabled = self.cur_well_known_multicast_status)

            if self.test_igmp_snooping:
                self.active_ap.set_igmp_snooping(self.wlan_if, enabled = self.cur_igmp_snooping_status)

            logging.info("Down %s interface on the active AP" % self.wlan_if)
            self.active_ap.set_state(self.wlan_if, 'down')
            time.sleep(2)

            if self.max_igmp_group or self.igmp_version:
                logging.info("Reboot AP to clear the current IGMP table")
                self.active_ap.reboot()
                time.sleep(5)
                self.active_ap.login() # re-login after reboot

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
        logging.info("---------- FINISH ----------")

    def _defineTestParams(self, conf):
        # multicast route setting
        self.multicast_network = "224.0.0.0"
        self.multicast_mask = "240.0.0.0"
        self.multicast_group = conf["multicast_group"]
        if conf.has_key('win_multicast_group'):
            self.win_mcast_group = conf['win_multicast_group']
        else: self.win_mcast_group = ""

        self.wlan_if = conf['wlan_if']

        self.remote_linux_sta = None
        self.remote_win_sta = None
        self.local_station = None
        self.active_ap = None
        self.active_ad_config = {}
        self.passive_ad_config = {} # Adapter used when verifying traffic sent to all stations

        # Iperf parameters
        if self.dead_station: self.timeout = "1800"
        else: self.timeout = "60"
        self.packet_len = '1400'
        self.ap_channel = conf['ap_channel']

        # tcpdump parameters:
        self.count = "500"
        self.proto = "udp"
        self.windump_info_file = ""
        self.tcpdump_info_file = ""

        # Port matching filter parameters
        self.proto = "udp"
        self.port = "5001"
        self.dest_port = True
        self.action = 'tos'

        self.bw_list = ['4m']

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
        self.local_sta_ip_addr, self.local_if_name = getLinuxIpAddr(self.local_station,
                                                                   self.testbed.sta_wifi_subnet, True)
        self.remote_linux_sta_ip_addr, self.remote_linux_if_name = getLinuxIpAddr(self.remote_linux_sta,
                                                                                 self.testbed.sta_wifi_subnet,
                                                                                 True)
        self.remote_win_sta_ip_addr, self.remote_win_if_name = getWinsIpAddr(self.remote_win_sta,
                                                                            self.testbed.sta_wifi_subnet,
                                                                            True)
        if not self.local_sta_ip_addr or not self.remote_linux_sta_ip_addr or not self.remote_win_sta_ip_addr:
            raise Exception("Can not find any ip address belongs to subnet %s" %
                            self.testbed.sta_wifi_subnet['network'])

        self.wireless_interface_ip_addr = getLinuxIpAddr(self.capture_station, self.testbed.sta_wireless_interface_info)
        if not self.wireless_interface_ip_addr:
            raise Exception("IP address of wireless interface on the linux station %s is not correct" %
                            conf['capture_station'])

    def _getADConfiguration(self, conf):

        # Get adapter configuration information
        self.active_ad_config = getADConfig(self.testbed,
                                            conf['active_ad'],
                                            self.testbed.ad_list)
        self.passive_ad_config = getADConfig(self.testbed,
                                             conf['passive_ad'],
                                             self.testbed.ad_list,
                                             "Passive AD")
        self.active_ad_mac = self.remote_linux_sta.get_ad_wireless_mac(self.active_ad_config)
        self.passive_ad_mac = self.remote_win_sta.get_ad_wireless_mac(self.passive_ad_config)
        self.ad_model = self.remote_linux_sta.get_ad_device_type(self.active_ad_config)

    def _saveConfig(self):
        logging.info("Save encryption information")
        self.current_ap_encryption = self.active_ap.get_encryption(self.wlan_if)
        self.current_ap_encryption['wlan_if'] = self.wlan_if

        self.current_active_ad_encryption = self.remote_linux_sta.get_ad_encryption(self.active_ad_config, 'wlan0')
        self.current_active_ad_encryption['wlan_if'] = 'wlan0'

        self.current_passive_ad_encryption = self.remote_win_sta.get_ad_encryption(self.passive_ad_config, 'wlan0')
        self.current_passive_ad_encryption['wlan_if'] = 'wlan0'

        # Save current QoS configuration
        logging.info("Save current QoS configuration on the active AP")
        if self.port_matching_filter:
            self.cur_port_match_status = saveCurPortMatchingFilterStatus(self.active_ap, self.eth_interface)

        self.cur_tos_classify_status = self.active_ap.get_tos_classification(self.eth_interface)
        if self.tos_matching:
            self.cur_tos_classify_value = saveToSValues(self.active_ap, self.media)

        logging.debug(self.active_ap.get_qos_cfg_option())
        if self.test_directed_multicast:
            self.cur_directed_mcast_status = self.active_ap.get_qos_cfg_option()['directed_multicast']

        if self.test_unknown_multicast_drop:
            self.cur_unknown_mcast_drop_status = self.active_ap.get_qos_cfg_option()['unknown_multicast_drop']
        if self.test_well_known_multicast:
            self.cur_well_known_multicast_status = self.active_ap.get_qos_cfg_option()['well_known_multicast_forward']
        if self.test_igmp_snooping:
            self.cur_igmp_snooping_status = self.active_ap.get_igmp_snooping(self.wlan_if)

    def _getQoSTestParams(self, conf):

        if conf.has_key('media'): self.media = conf['media']
        else: self.media = ""
        if conf.has_key('queue'): self.queue = conf['queue']
        else: self.queue = ""
        if conf.has_key('tos_classify_value'): self.tos_classify_value = conf['tos_classify_value']
        else: self.tos_classify_value = ""
        if conf.has_key('tos_matching'): self.tos_matching = conf['tos_matching']
        else: self.tos_matching = False
        if conf.has_key('profile'): self.profile = conf['profile']
        else: self.profile = ""
        if conf.has_key('dead_station'): self.dead_station = conf['dead_station']
        else: self.dead_station = False
        if conf.has_key('heuristics_enable'):
            self.heuristics_enable = conf['heuristics_enable']
        else: self.heuristics_enable = True

        if conf.has_key('tos_classify_enable'):
            self.tos_classify_enable = conf['tos_classify_enable']
        else:
            self.tos_classify_enable = True
        if conf.has_key('directed_multicast'):
            self.test_directed_multicast = True
            self.directed_multicast = conf['directed_multicast']
        else: self.test_directed_multicast = False

        if conf.has_key('unknown_mcast_drop'):
            self.test_unknown_multicast_drop = True
            self.unknown_multicast_drop = conf['unknown_mcast_drop']
        else: self.test_unknown_multicast_drop = False

        if conf.has_key('igmp_snooping'):
            self.test_igmp_snooping = True
            self.igmp_snooping = conf['igmp_snooping']
        else: self.test_igmp_snooping = False

        if conf.has_key('well_known_multicast'):
            self.test_well_known_multicast = True
            self.well_known_multicast = conf['well_known_multicast']
        else: self.test_well_known_multicast = False

        if conf.has_key('unknown_multicast_group'):
            self.unknown_multicast_group = conf['unknown_multicast_group']
        if conf.has_key('multicast_address_src'):
            self.multicast_address_src = conf['multicast_address_src']
        if conf.has_key('multicast_address_dst'):
            self.multicast_address_dst = conf['multicast_address_dst']
        if conf.has_key('max_igmp_group'):
            self.max_igmp_group = conf['max_igmp_group']
        else: self.max_igmp_group = ""
        if conf.has_key('packet_replay_file'):
            self.packet_replay_file = conf['packet_replay_file']
        else: self.packet_replay_file = ""
        if conf.has_key('igmp_version'):
            self.igmp_version = conf['igmp_version']
        else: self.igmp_version = ""
        if conf.has_key('port_matching_filter'):
            self.port_matching_filter = conf['port_matching_filter']
        else: self.port_matching_filter = False

        if conf.has_key('stream_with_multi_sta'):
            self.stream_with_multi_sta = conf['stream_with_multi_sta']
        else: self.stream_with_multi_sta = False

        if conf.has_key('stream_with_same_group'):
            self.stream_with_same_group = conf['stream_with_same_group']
        else: self.stream_with_same_group = False

        if conf.has_key('verify_igmp_query'):
            self.verify_igmp_query = conf['verify_igmp_query']
        else: self.verify_igmp_query = False

    def _streamMulticastTraffic(self):

        for bw in self.bw_list:
            logging.info("Stream traffic with bandwidth %sbps" % bw.upper())
            # Send some learning packet
            verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_linux_sta_ip_addr)

            logging.info("Start iperf server on the station %s" % self.remote_linux_sta_ip_addr)
            self.remote_linux_sta.start_iperf(serv_addr = self.multicast_group,
                                             test_udp = True,
                                             multicast_srv = True)

            if self.stream_with_multi_sta:
                verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_win_sta_ip_addr)
                logging.info("Start iperf server on the station %s" % self.remote_win_sta_ip_addr)
                if not self.stream_with_same_group:
                    self.remote_win_sta.start_iperf(serv_addr = self.win_mcast_group,
                                                   test_udp = True,
                                                   multicast_srv = True)
                else:
                    self.remote_win_sta.start_iperf(serv_addr = self.multicast_group,
                                                   test_udp = True,
                                                   multicast_srv = True)

            # Capture traffic on the remote stations
            if self.tos_classify_value or self.dead_station: self._startTcpdump()
            if self.test_directed_multicast:
                self._start_windump(self.multicast_group)
                self._startTcpdump()

            if self.test_unknown_multicast_drop:
                self._startTcpdump()
                self._start_windump(self.unknown_multicast_group)

            logging.info("Clear media queue statistics on the active ap")
            self.active_ap.clear_mqstats(self.wlan_if)
            time.sleep(1)

            if self.dead_station:
                self.cur_dead_station_count = 0
                self.cur_dead_station_count = self.active_ap.get_dead_station_count()
                logging.info("Current dead station count: %d" % self.cur_dead_station_count)
                self._start_iperf(self.multicast_group, bw)
                time.sleep(30)

                # Analyze capturing traffic
                self.remote_linux_sta.stop_tcp_dump()
                capture_ok = findCapturedPacket(self.remote_linux_sta,
                                                self.tcpdump_info_file,
                                                self.local_sta_ip_addr,
                                                self.multicast_group)
                if not capture_ok:
                    msg = "Can not capture traffic with source ip address %s " % self.local_sta_ip_addr
                    msg += " and destination ip address %s while streaming traffic" % self.multicast_group
                    return ["FAIL", msg]
                logging.info("Station %s received traffic correctly" % self.remote_linux_sta_ip_addr)

                logging.info("Disconnect adapter on remote linux station to verify dead station count")
                self.remote_linux_sta.set_ruckus_ad_state(self.active_ad_config, 'down', 'wlan0')
                time.sleep(10)
                verifyStaConnection(self.local_station,
                                    self.local_sta_ip_addr,
                                    self.remote_linux_sta_ip_addr,
                                    5000, False)

                new_dead_station_count_value = self.active_ap.get_dead_station_count()
                logging.info("New dead station count value: %d" % new_dead_station_count_value)
                if  new_dead_station_count_value <= self.cur_dead_station_count:
                    logging.info("Kill iperf client processes")
                    self.local_station.stop_iperf()
                    return ["FAIL", "Dead station count didn't change when a station disconnected during the streaming"]
                else:
                    logging.info("Kill iperf client processes")
                    self.local_station.stop_iperf()
                    return ["PASS", ""]

            if self.test_unknown_multicast_drop:
                msg = "Verify that multicast group %s is not added in the IGMP talbe. " % self.unknown_multicast_group
                msg += "So that it is unknown multicast group"
                logging.info(msg)
                found_igmp_entry = get_igmp_table(self.active_ap, self.unknown_multicast_group)
                if not found_igmp_entry:
                    logging.info("Entry %s is not found in IGMP table" % self.unknown_multicast_group)
                else:
                    return ["FAIL","%s entry was added to IGMP table. It is not an unknown multicast group" %
                            self.unknown_multicast_group]
                self._start_iperf(self.unknown_multicast_group, bw)
            else:
                found_igmp_entry = get_igmp_table(self.active_ap, self.multicast_group)
                if self.test_igmp_snooping:
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

                if self.stream_with_multi_sta:
                    if self.stream_with_same_group:
                        self._start_iperf(self.multicast_group, bw)
                    else:
                        self._start_iperf(self.win_mcast_group, bw)
                        self._start_iperf(self.multicast_group, bw)
                        time.sleep(4)
                else:
                    self._start_iperf(self.multicast_group, bw)
                time.sleep(10)

                # Capture traffic over the air
                if not self.stream_with_multi_sta:
                    if self.ad_model.lower() != "vf7111":
                        fd, tshark_info_file = tempfile.mkstemp(".txt")
                        logging.info("Use tshark to capture traffic over the air")
                        self.capture_station.capture_traffic_ota(ip_addr = self.wireless_interface_ip_addr,
                                                               filename = tshark_info_file,
                                                               expression = "ether host",
                                                               host = self.bssid,
                                                               count = self.count)
            time.sleep(int(self.timeout) - 5)

            # Get mq statistics on the linux station
            active_ad_mqstat = getStaMQStatistics(self.active_ap, self.active_ad_mac, self.wlan_if)
            if self.port_matching_filter:
                msg = "Verify that although incoming traffic that matches with Port Match rule, "
                msg += "it's not affected by this rule. Traffic will be inserted to the video queue"
                logging.info(msg)

            # Get traffic information on each queue
            active_ad_queue_info, active_ad_empty_queues, active_ad_empty_deq = get_mqstatsInfo(active_ad_mqstat,
                                                                                               self.queue)

            # If streaming traffic to multiple stations
            if self.stream_with_multi_sta:
                passive_ad_mqstat = getStaMQStatistics(self.active_ap, self.passive_ad_mac, self.wlan_if)
                passive_ad_queue_info, passive_ad_empty_queues, passive_ad_empty_deq = get_mqstatsInfo(passive_ad_mqstat,
                                                                                                      self.queue)

            if self.test_unknown_multicast_drop:
                # If unknown multicast drop is enable, when streaming traffic to this group, traffic will be dropped
                self.remote_win_sta.stop_windump()
                self.remote_linux_sta.stop_tcp_dump()
                win_cap_res, linux_cap_res = self._getCapturedPacket(self.unknown_multicast_group)
                if self.unknown_multicast_drop:
                    res, msg = verifyEmptyQueue(active_ad_mqstat)
                    if res == "FAIL": return [res, msg]

                    if win_cap_res or linux_cap_res:
                        msg = "Stations still receive unknown multicast packets "
                        msg += "from AP while unknow multicast drop is enabled"
                        return ["FAIL", msg]
                    else: logging.info("Station does not receive unknown traffic because unknown multicast drop is enabled")
                else:
                    # Verify MQ Statistics
                    logging.info("Verify that traffic will be inserted to the %s queue" % self.queue)
                    res, msg = verifyMQStats(self.queue,
                                             active_ad_queue_info,
                                             active_ad_empty_queues,
                                             active_ad_empty_deq,
                                             self.timeout,
                                             self.active_ad_mac)
                    if res == "FAIL": return [res, msg]
                    if not linux_cap_res or not win_cap_res:
                        return ["FAIL", "Stations do not receive traffic from group %s while unknown multicast drop is disabled"
                                % self.unknown_multicast_group]
                    else: logging.info("Stations can receive unknown traffic because unknown multicast drop is disabled")
            else:
                if self.test_igmp_snooping:
                    if not self.igmp_snooping:
                        res, msg = verifyEmptyQueue(active_ad_mqstat)
                        if res == "FAIL": return [res, msg]
                else:
                    # Verify MQ Statistics
                    logging.info("Station %s: verify that traffic will be inserted to the %s queue" %
                                 (self.active_ad_mac, self.queue))
                    res, msg = verifyMQStats(self.queue,
                                             active_ad_queue_info,
                                             active_ad_empty_queues,
                                             active_ad_empty_deq,
                                             self.timeout,
                                             self.active_ad_mac)
                    if res == "FAIL":
                        return [res, msg]

                    if self.stream_with_multi_sta:
                        logging.info("Station %s: verify that traffic will be inserted to the %s queue" %
                                     (self.passive_ad_mac, self.queue))
                        res, msg = verifyMQStats(self.queue,
                                                 passive_ad_queue_info,
                                                 passive_ad_empty_queues,
                                                 passive_ad_empty_deq,
                                                 self.timeout,
                                                 self.passive_ad_mac)
                        if res == "FAIL":
                            return [res, msg]

                    # Analyze traffic over the air
                    if not self.stream_with_multi_sta:
                        if self.ad_model.lower() != 'vf7111':
                            res, msg = analyzeTrafficOTA(tshark_info_file,
                                                         self.capture_station,
                                                         self.local_sta_ip_addr,
                                                         self.multicast_group,
                                                         self.queue)
                            if res == "FAIL": return [res, msg]

            # Verify ToS value of traffic at receiver
            if self.tos_classify_value:
                res, msg = verifyToSValue(self.tcpdump_info_file,
                                          self.remote_linux_sta,
                                          self.local_sta_ip_addr,
                                          self.multicast_group,
                                          self.tos_classify_value)

            # Analyze traffic after capturing on stations in case testing directed multicast feature
            if self.test_directed_multicast:
                logging.info("Verify that if all stations can receive traffic")
                self.remote_win_sta.stop_windump()
                win_cap_res, linux_cap_res = self._getCapturedPacket(self.multicast_group)
                if not self.directed_multicast:
                    if not win_cap_res:
                        return ["FAIL", "Station %s does not receive traffic in case directed multicast is disabled" %
                                self.remote_win_sta_ip_addr]
                    if not linux_cap_res:
                        return ["FAIL", "Station %s does not receive traffic in case directed multicast is disabled" %
                                self.remote_linux_sta_ip_addr]
                    logging.info("All stations can receive traffic because directed multicast is disabled")
                else:
                    if not win_cap_res:
                        msg = "Station %s can not receive traffic because it does not " % self.remote_win_sta_ip_addr
                        msg += "join the multicast group %s" % self.multicast_group
                        logging.info(msg)
                    else:
                        return ["FAIL", "Station %s can receive traffic while it does not join the multicast group %s" %
                                (self.remote_win_sta_ip_addr, self.multicast_group)]
                    if not linux_cap_res:
                        return ["FAIL", "Station %s does not receive traffic while it is joining the multicast group %s" %
                                (self.remote_linux_sta_ip_addr, self.multicast_group)]
                    else:
                        logging.info("Station %s receives traffic successfully" % self.remote_linux_sta_ip_addr)

        return ["PASS", ""]

    def _start_iperf(self, dst_ip, bandwidth = ""):
        logging.info("Start multicast streaming from local station[%s] to [%s]" %
                     (self.local_sta_ip_addr, dst_ip))
        self.local_station.start_iperf(serv_addr = dst_ip,
                                      test_udp = True,
                                      packet_len = self.packet_len,
                                      timeout = self.timeout,
                                      bw = bandwidth,
                                      tos = self.tos_classify_value)

    def _start_windump(self, host):
        logging.info("Use tool windump to capture traffic on the windows station %s" % self.remote_win_sta_ip_addr)
        self.windump_info_file = "windump_capture.dmp"
        self.remote_win_sta.start_windump_for_ap(ip_addr = self.remote_win_sta_ip_addr,
                                                 proto = "",
                                                 count = "30",
                                                 file_path = self.windump_info_file,
                                                 host = host)

    def _startTcpdump(self):
        logging.info("Use tool tcpdump to capture traffic on the remote station %s" % self.remote_linux_sta_ip_addr)
        fo, self.tcpdump_info_file = tempfile.mkstemp(".txt")
        if self.test_unknown_multicast_drop: self.count = '40'
        self.remote_linux_sta.start_tcp_dump(ip_addr = self.remote_linux_sta_ip_addr,
                                           proto = self.proto,
                                           count = self.count,
                                           file_path = self.tcpdump_info_file)

    def _getCapturedPacket(self, dst_ip_addr, src_ip_addr = ""):
        if src_ip_addr: src_temp = src_ip_addr
        else: src_temp = self.local_sta_ip_addr

        win_cap_res = findCapturedPacket(self.remote_win_sta,
                                         self.windump_info_file, src_temp, dst_ip_addr)
        linux_cap_res = findCapturedPacket(self.remote_linux_sta,
                                           self.tcpdump_info_file, src_temp, dst_ip_addr)
        return win_cap_res, linux_cap_res

