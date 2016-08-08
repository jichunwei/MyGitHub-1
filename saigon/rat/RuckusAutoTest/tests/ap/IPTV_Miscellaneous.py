# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: IPTV_Miscellaneous class tests ability of queuing traffic when streaming with the given conditions.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):
    1. Build under test is loaded on the AP

    Required components: RuckusAP, StationLinuxPC
    Test parameters: {'active_ap': 'ip address of active ap',
                             'remote_station': 'ip address of remote linux pc',
                             'local_station': 'ip address of local linux pc',
                             'active_ad': 'ip address of active adapter',
                             'verify_igmp_query':'decide if AP forwards IGMP Query packets to Adapters',
                             'use_vlan':'decide if vlan is configured on AP',
                             'vlan_tagged':'decide if traffic is tagged',
                             'vlan_untagged':'decide if traffic is untagged',
                             'streaming':'decide if test case will stream traffic or not',
                             'multicast':'decide if traffic is multicast',
                             'queue':'queue name',
                             'heuristics':'decide if test case is testing heuristics',
                             'verify_tos':'decide if traffic is streamed with ToS or not',
                             'use_tcp_proto':'decide if Port Matching Filter uses TCP or UDP',
                             'port_matching':'If it is True, traffic will be matched with Port Matching Filter'
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
        - Change Vlan/QoS configuration option on the AP with information get from test parameters.
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
import libIPTV_TestConfig as tconfig
import libIPTV_TestMethods as tmethod

class IPTV_Miscellaneous(Test):
    required_components = ['RuckusAP', 'StationLinuxPC', "StationWinPC"]
    parameter_description = {'active_ap': 'ip address of active ap',
                             'remote_station': 'ip address of remote linux pc',
                             'local_station': 'ip address of local linux pc',
                             'active_ad': 'ip address of active adapter',
                             'verify_igmp_query':'decide if AP forwards IGMP Query packets to Adapters',
                             'use_vlan':'decide if vlan is configured on AP',
                             'vlan_tagged':'decide if traffic is tagged',
                             'vlan_untagged':'decide if traffic is untagged',
                             'streaming':'decide if test case will stream traffic or not',
                             'multicast':'decide if traffic is multicast',
                             'queue':'queue name',
                             'heuristics':'decide if test case is testing heuristics',
                             'verify_tos':'decide if traffic is streamed with ToS or not',
                             'use_tcp_proto':'decide if Port Matching Filter uses TCP or UDP',
                             'port_matching':'If it is True, traffic will be matched with Port Matching Filter'
    }

    def config(self, conf):
        self._defineTestParams(conf)
        self._getStations(conf)
        self._get_ip_addrs(conf)
        self._getActiveAP(conf)
        self._getADConfig(conf)
        self._saveConfig()

        if self.port_matching:
            logging.info("Remove port matching filter")
            self.active_ap.remove_port_matching_rule(self.ap_eth_interface)

        if self.use_vlan:
            logging.info("Remove all VLANs out of the active AP")
            self.active_ap.remove_all_vlan()

            # Define ethernet port list for VLAN
            eth_list = self.active_ap.get_all_eth_interface()
            temp = []
            for eth in eth_list:
                temp.append(str(self._getIntfNum(eth['interface'])))
            self.eth_port_list = " ".join(temp)

            # Get interface name that's used to control AP on local station
            if not self.vlan_tagged:
                ap_net = get_network_address(self.ap_ip_addr)
                ctrl_ap_ip, self.ctrl_ap_ifname = tconfig.getLinuxIpAddr(self.local_station, ap_net, True)
                self.ap_cur_ip_addr = self.ap_ip_addr

    def test(self):
        self._cfg_wlan(self.wlan_if)
        self._cfg_wlan(self.wlan_if, False, self.ad_linux_ip_addr,
                         self.remote_linux_sta, self.ad_linux_conf)

        tmethod.setADWlanState(self.remote_linux_sta,
                               self.ad_linux_conf, "up",
                               self.ad_model, self.ad_linux_ip_addr)

        if int(self.ap_channel) >= 52 and int(self.ap_channel) <= 140:
            dfs_info = self.active_ap.get_dfs_info(self.wlan_if)
            if dfs_info['enable']:
                start_time = time.time()
                while time.time() - start_time < dfs_info['cactime']:
                    bssid = tmethod.getBSSID(self.active_ap, self.wlan_if)
                    if bssid != "00:00:00:00:00:00": break

        # Verify connection between stations
        tmethod.verifyStaConnection(self.local_station,
                                    self.local_sta_ip_addr, self.remote_linux_ip_addr)

        # If script verifies IGMP query
        if self.verify_igmp_query:
            logging.info("Verify that AP can receive and transmit IGMP query to Adapters")
            self._startTcpdump(self.remote_linux_ip_addr, 'igmp')

            # Using tcpreplay to simulate igmp query packets
            self.local_station.start_tcp_replay(if_name = self.local_ifname,
                                              file_name = self.igmp_query_file,
                                              rate = "0.3")
            time.sleep(3)
            self.remote_linux_sta.stop_tcp_dump()
            capture_res = tmethod.findCapturedPacket(self.remote_linux_sta,
                                                     self.tcpdump_info,
                                                     self.src_igmp_query,
                                                     self.allhost_mcast,
                                                     "igmp query", False)

            if not capture_res: return ["FAIL", "Station does not receive IGMP query"]
            else: return ["PASS", ""]

        if self.verify_tos:
            logging.info("Configure ToS classify value [%s] for %s queue" % (self.tos_value, self.queue))
            self.active_ap.set_tos_values(self.queue, self.tos_value)

        if self.port_matching:
            msg = "Add Port Matching Filter to the AP: proto ---> %s, port ---> %s, " % (self.proto, self.port)
            msg += "action ---> %s, media ---> %s" % (self.action, self.queue)
            logging.info(msg)
            if self.use_tcp_proto:
                self.active_ap.add_port_matching_rule(self.ap_eth_interface, self.proto,
                                                   self.action, self.port,
                                                   True, self.queue)
                self.active_ap.add_port_matching_rule(self.ap_eth_interface, self.proto,
                                                   self.action, self.port,
                                                   False, self.queue)
            else:
                self.active_ap.add_port_matching_rule(self.ap_eth_interface, self.proto,
                                                   self.action, self.port,
                                                   True, self.queue)
        if self.heuristics:
            logging.info("Configure parameters for heuristics algorithm: ")
            if self.queue == 'voice':
                logging.info("Packet length ----> %s, packet gap ----> %s" % (self.voice_pktlen, self.voice_pktgap))
                self.active_ap.set_heuristics_cfg(self.queue,
                                                   cfg_pktgap = True,
                                                   min_value = self.voice_pktgap[0],
                                                   max_value = self.voice_pktgap[1])
                self.active_ap.set_heuristics_cfg(self.queue,
                                                   cfg_pktlen = True,
                                                   min_value = self.voice_pktlen[0],
                                                   max_value = self.voice_pktlen[1])
            else:
                logging.info("Packet length ----> %s, packet gap ----> %s" % (self.video_pktlen, self.video_pktgap))
                self.active_ap.set_heuristics_cfg(self.queue,
                                                   cfg_pktgap = True,
                                                   min_value = self.video_pktgap[0],
                                                   max_value = self.video_pktgap[1])
                self.active_ap.set_heuristics_cfg(self.queue,
                                                   cfg_pktlen = True,
                                                   min_value = self.video_pktlen[0],
                                                   max_value = self.video_pktlen[1])

        if self.use_vlan:
            if not self.vlan_tagged:
                time.sleep(2)
                # This case is untagged vlan testing. On AP will create a vlan with untagged ethernet port.
                # This causes Test Engine has no way to be able to control AP
                # so that we need to create another tagged vlan on both AP and TestEngine,
                # then TestEngine can telnet to AP by this way
                self.ctrl_ap_ifname = self.local_station.add_vlan(self.ctrl_ap_ifname,
                                                                 self.mgmt_vlan_id,
                                                                 self.ctrl_ap_ip_addr)
                self.active_ap.create_vlan(dict(vlan_id=self.mgmt_vlan_id,
                                               eth_tagged_port=self.eth_port_list)
                )
                res, msg = self.active_ap.add_ip_to_brd_intf("br0.%s" % self.mgmt_vlan_id, self.ap_mgmt_vlan_ip_addr)
                if not res:
                    raise Exception(msg)
                # From now, TestEngine will telnet to AP by new ip_addr
                self.active_ap.ip_addr = self.ap_mgmt_vlan_ip_addr

            # Get vlan parameters
            vlan_cfg = self._defineVlanParams(self.eth_port_list,
                                              self._getIntfNum(self.wlan_if), self.vlan_id, self.vlan_tagged)

            logging.info("Create a VLAN %s on the AP" % self.vlan_id)
            self.active_ap.create_vlan(vlan_cfg)
            time.sleep(3)

            if self.vlan_tagged:
                # Add vlan on the local linux station
                local_vlan_ip_addr = "%s.%s.%s" % (self.net_prefix, self.vlan_id,
                                                  str(self.local_sta_ip_addr.split('.')[-1]))
                self.vlan_if = self.local_station.add_vlan(self.local_ifname, self.vlan_id, local_vlan_ip_addr)

                # Add ip_addr to subinterface
                remote_vlan_ip_addr = "%s.%s.%s" % (self.net_prefix, self.vlan_id,
                                                   str(self.remote_linux_ip_addr.split('.')[-1]))
                self.remote_linux_subif = self.remote_linux_sta.add_sub_intf(self.remote_linux_ifname,
                                                                           remote_vlan_ip_addr, self.vlan_id)
                # Verify connection between stations
                tmethod.verifyStaConnection(self.remote_linux_sta,
                                            remote_vlan_ip_addr, local_vlan_ip_addr)

                # Add mcast route
                if self.multicast:
                    self._addMcastRoute(self.vlan_if, self.remote_linux_subif)
                    res, msg = self._streamTraffic(local_vlan_ip_addr, self.mcast_group, remote_vlan_ip_addr)
                    if res == "FAIL": return res, msg
                if self.heuristics or self.port_matching:
                    res, msg = self._streamTraffic(local_vlan_ip_addr, remote_vlan_ip_addr, remote_vlan_ip_addr)
                    if res == "FAIL": return res, msg
            else:
                time.sleep(1)
                if self.multicast:
                    self._addMcastRoute(self.local_ifname, self.remote_linux_ifname)
                    res, msg = self._streamTraffic(self.local_sta_ip_addr, self.mcast_group, self.remote_linux_ip_addr)
                    if res == "FAIL": return res, msg
                if self.heuristics or self.port_matching:
                    res, msg = self._streamTraffic(self.local_sta_ip_addr, self.remote_linux_ip_addr, self.remote_linux_ip_addr)
                    if res == "FAIL": return res, msg
        else:
            if self.use_tcp_proto:
                res, msg = self._streamTraffic(self.local_sta_ip_addr, self.remote_linux_ip_addr, self.remote_linux_ip_addr)
                if res == "FAIL": return res, msg

        return ["PASS", ""]

    def cleanup(self):
        if self.active_ap:
            if self.use_vlan:
                self.active_ap.remove_vlan(self.vlan_id)
                time.sleep(2)
                if not self.vlan_tagged:
                    self.active_ap.ip_addr = self.ap_cur_ip_addr
                    self.active_ap.remove_vlan(self.mgmt_vlan_id)
                    # Reboot AP to remove all sub bridge interfaces that related to created VLANs
                    self.active_ap.reboot()
                    time.sleep(5)
                    self.active_ap.login() # re-login after reboot

            if self.port_matching:
                logging.info("Remove port matching filter")
                self.active_ap.remove_port_matching_rule(self.ap_eth_interface)

            if self.verify_tos:
                logging.info("Return the previous ToS value for %s" % self.queue)
                self.active_ap.set_tos_values(self.queue, self.cur_tos_classify_value)

            if self.heuristics:
                logging.info("Return the previous configuration for heuristics")
                pkg_min = self.heuristics_info['packet_gap'][self.queue][0]
                pkg_max = self.heuristics_info['packet_gap'][self.queue][1]
                pklen_min = self.heuristics_info['packet_len'][self.queue][0]
                pklen_max = self.heuristics_info['packet_len'][self.queue][1]

                self.active_ap.set_heuristics_cfg(self.queue,
                                                   cfg_pktlen = True,
                                                   min_value = pklen_min,
                                                   max_value = pklen_max)

                self.active_ap.set_heuristics_cfg(self.queue,
                                                   cfg_pktgap = True,
                                                   min_value = pkg_min,
                                                   max_value = pkg_max)

            logging.info("Down %s interface on the active AP" % self.wlan_if)
            self.active_ap.set_state(self.wlan_if, 'down')
            self.active_ap.cfg_wlan(self.cur_ap_encrypt)
            time.sleep(2)

        if self.remote_linux_sta and self.local_station:
            tmethod.setADWlanState(self.remote_linux_sta,
                                   self.ad_linux_conf, "down",
                                   self.ad_model, self.ad_linux_ip_addr)
            self.remote_linux_sta.cfg_wlan(self.ad_linux_conf, self.cur_ad_linux_encrypt)

            if self.use_vlan:
                if self.vlan_tagged:
                    if self.multicast:
                        self._delMcastRoute(self.vlan_if, self.remote_linux_subif)
                    self.remote_linux_sta.rem_sub_intf(self.remote_linux_subif)
                    self.local_station.rem_vlan(self.vlan_if)
                else:
                    if self.multicast:
                        self._delMcastRoute(self.local_ifname, self.remote_linux_ifname)
                    self.local_station.rem_vlan(self.ctrl_ap_ifname)

            if self.heuristics:
                logging.info("Kill zing server process on the local station %s" % self.local_sta_ip_addr)
                self.local_station.stop_zing()
            else:
                logging.info("Kill iperf client processes")
                self.remote_linux_sta.stop_iperf()

        logging.info("---------- FINISH ----------")

    def _saveConfig(self):
        # Save encryption information
        self.cur_ap_encrypt = self.active_ap.get_encryption(self.wlan_if)
        self.cur_ap_encrypt['wlan_if'] = self.wlan_if

        self.cur_ad_linux_encrypt = self.remote_linux_sta.get_ad_encryption(self.ad_linux_conf, 'wlan0')
        self.cur_ad_linux_encrypt['wlan_if'] = 'wlan0'

        if self.heuristics:
            self.heuristics_info = self.active_ap.get_heuristics_cfg()
        if self.verify_tos:
            self.cur_tos_classify_value = tconfig.saveToSValues(self.active_ap, self.queue)

    def _startTcpdump(self, received_ip, proto = 'udp'):
        logging.info("Use tool tcpdump to capture traffic on the Linux station %s" % received_ip)
        fo, self.tcpdump_info = tempfile.mkstemp(".txt")
        self.remote_linux_sta.start_tcp_dump(ip_addr = received_ip,
                                           proto = proto,
                                           count = self.count,
                                           file_path = self.tcpdump_info)

    def _cfg_wlan(self, wlan_if = "", on_ap = True, ad_ip_addr = "", sta_obj = None, ad_config = {}):
        wlan_cfg = dict(auth="open",
                        encryption="none",
                        ssid='IPTV_%s' % wlan_if,
                        wlan_if='%s' % wlan_if)
        if on_ap:
            logging.info("Configure a WLAN with SSID %s on the active AP" % wlan_cfg['ssid'])
            self.active_ap.cfg_wlan(wlan_cfg)
        else:
            ad_wlan_cfg = wlan_cfg.copy()
            ad_wlan_cfg['wlan_if'] = 'wlan0'
            logging.info("Configure a WLAN with SSID %s on Adapter %s" % (wlan_cfg['ssid'], ad_ip_addr))
            sta_obj.cfg_wlan(ad_config, ad_wlan_cfg)

    def _defineTestParams(self, conf):
        logging.info('Test cfg: %s' % pformat(conf))
        self.mcast_net = "224.0.0.0"
        self.mcast_mask = "240.0.0.0"
        self.timeout = '90'

        if conf.has_key('verify_igmp_query'):
            self.verify_igmp_query = conf['verify_igmp_query']
            self.igmp_query_file = conf['igmp_query_file']
            self.src_igmp_query = conf['src_igmp_query']
            self.allhost_mcast = conf['allhost_mcast']
        else: self.verify_igmp_query = False

        if conf.has_key('use_vlan'):
            self.use_vlan = conf['use_vlan']
            self.vlan_tagged = conf['vlan_tagged']
            self.vlan_id = '150'
            self.vlan_if = ''
            self.remote_linux_subif = ''
            self.net_prefix = '192.168'
            if not self.vlan_tagged:
                self.ctrl_ap_ifname = ''
                self.ap_mgmt_vlan_ip_addr = '192.168.200.100'
                self.ctrl_ap_ip_addr = '192.168.200.200'
                self.mgmt_vlan_id = '200'
        else: self.use_vlan = False

        if conf.has_key('streaming'):
            self.streaming = conf['streaming']
            self.queue = conf['queue']
        else: self.streaming = False

        if conf.has_key('multicast'):
            self.multicast = conf['multicast']
        else: self.multicast = False

        if conf.has_key('mcast_group'):
            self.mcast_group = conf['mcast_group']
        else: self.mcast_group = ""

        if conf.has_key('heuristics'):
            self.heuristics = conf['heuristics']
        else: self.heuristics = False

        if conf.has_key('verify_tos'):
            self.verify_tos = conf['verify_tos']
        else: self.verify_tos = False

        if conf.has_key('tos_value'):
            self.tos_value = conf['tos_value']
        else: self.tos_value = ''

        if conf.has_key('port_matching'):
            self.port_matching = conf['port_matching']
            self.proto = conf['proto']
            self.action = conf['action']
            self.port = conf['port']
        else: self.port_matching = False

        if conf.has_key('use_tcp_proto'):
            self.use_tcp_proto = conf['use_tcp_proto']
        else: self.use_tcp_proto = False

        self.wlan_if = conf['wlan_if']
        self.ap_channel = conf['ap_channel']

        self.remote_linux_sta = None
        self.remote_win_sta = None
        self.local_station = None
        self.active_ap = None
        self.ad_linux_conf = {}
        self.ad_win_conf = {}

        # tcpdump info
        self.tcpdump_info = ""
        self.count = "40"

        # Heuristics values
        self.video_pktgap = ['5', '85']
        self.video_pktlen = ['900', '1500']
        self.voice_pktgap = ['30', '200']
        self.voice_pktlen = ['60', '500']

    def _getStations(self, conf):
        # Find exactly stations
        station_list = self.testbed.components['Station']
        self.remote_linux_sta = tconfig.getStation(conf['remote_linux_sta'], station_list)
        self.local_station = tconfig.getStation(conf['local_station'], station_list)

    def _get_ip_addrs(self, conf):

        error_msg = "Can not find any ip addresses belong to subnet %s" % self.testbed.sta_wifi_subnet['network']

        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        self.ad_linux_ip_addr = self.testbed.getAdIpAddrBySymName(conf['ad_linux'])

        # Find the ip address of interface that connected to the adapter on the local station and remote station
        self.local_sta_ip_addr, self.local_ifname = tconfig.getLinuxIpAddr(self.local_station,
                                                                          self.testbed.sta_wifi_subnet, True)
        self.remote_linux_ip_addr, self.remote_linux_ifname = tconfig.getLinuxIpAddr(self.remote_linux_sta,
                                                                                    self.testbed.sta_wifi_subnet, True)
        if not self.local_sta_ip_addr or not self.remote_linux_ip_addr:
            raise Exception("[Linux STAs]: %s" % error_msg)

    def _getActiveAP(self, conf):
        logging.info("Find the active AP object")
        self.active_ap = tconfig.getTestbedActiveAP(self.testbed, conf['active_ap'],
                                                    self.testbed.components['AP'],
                                                    self.ap_channel,
                                                    self.wlan_if)
        self.ap_eth_interface = self.active_ap.get_eth_inferface_name()

    def _getADConfig(self, conf):

        # Get adapter configuration information
        self.ad_linux_conf = tconfig.getADConfig(self.testbed,
                                                 conf['ad_linux'],
                                                 self.testbed.ad_list,
                                                 "AD behind Linux")
        self.ad_linux_mac = self.remote_linux_sta.get_ad_wireless_mac(self.ad_linux_conf)
        self.ad_model = self.remote_linux_sta.get_ad_device_type(self.ad_linux_conf)

    def _defineVlanParams(self, eth_port_list, wlan_if, vlan_id, tagged = True):

        vlan_cfg = dict(vlan_name="ChowChow",
                        native_wlan=wlan_if,
                        vlan_id=vlan_id)
        if tagged: vlan_cfg['eth_tagged_port'] = eth_port_list
        else: vlan_cfg['eth_native_port'] = eth_port_list

        return vlan_cfg

    def _addMcastRoute(self, local_interface, remote_interface):
        self.local_station.set_route("add", self.mcast_net, self.mcast_mask, local_interface)
        self.remote_linux_sta.set_route("add", self.mcast_net, self.mcast_mask, remote_interface)

    def _delMcastRoute(self, local_interface, remote_interface):
        logging.info("Delete Multicast Route")
        self.local_station.set_route("del", self.mcast_net, self.mcast_mask, local_interface)
        self.remote_linux_sta.set_route("del", self.mcast_net, self.mcast_mask, remote_interface)

    def _start_iperf(self, src_ip, dst_ip, tos = '', bw = '4m'):
        logging.info("Start multicast streaming from local station[%s] to [%s]" %
                     (src_ip, dst_ip))
        self.local_station.start_iperf(serv_addr = dst_ip, test_udp = True,
                                      timeout = self.timeout, bw = bw, tos = tos)

    def _streamTraffic(self, src_ip, dst_ip, received_ip):

        if self.multicast:
            logging.info("Start iperf server on the station %s" % self.remote_linux_ip_addr)
            self.remote_linux_sta.start_iperf(serv_addr = dst_ip, test_udp = True, multicast_srv = True)
            time.sleep(2)

            found_igmp_entry = tmethod.get_igmp_table(self.active_ap, dst_ip)
            if not found_igmp_entry:
                return ["FAIL","%s entry wasn't added to IGMP table" % dst_ip]
            logging.info("Found %s entry in IGMP table" % dst_ip)

        if self.port_matching:
            logging.info("Start iperf server on the station %s" % self.remote_linux_ip_addr)
            if self.use_tcp_proto:
                self.remote_linux_sta.start_iperf(test_udp = False)
            else: self.remote_linux_sta.start_iperf(test_udp = True)

        if self.heuristics:
            logging.info("Start zing server on the local station %s" % src_ip)
            self.local_station.start_zing(test_udp = True)

        logging.info("Clear media queue statistics on the active ap")
        self.active_ap.clear_mqstats(self.wlan_if)
        time.sleep(1)

        if not self.use_tcp_proto: self._startTcpdump(received_ip)

        if self.heuristics:
            logging.info("Start to stream traffic from the station %s to the remote station %s" % (src_ip, dst_ip))
            if self.queue == "voice":
                zing_pktgap = (int(self.voice_pktgap[0]) + 10) * 1000
                zing_pktlen = int(self.voice_pktlen[0]) + 10
            else:
                zing_pktgap = (int(self.video_pktgap[0]) + 10) * 1000
                zing_pktlen = int(self.video_pktlen[0]) + 10
            self.remote_linux_sta.start_zing(server_addr=src_ip,
                                            pkt_gap = zing_pktgap,
                                            pkt_len = zing_pktlen,
                                            test_udp = True,
                                            timeout = self.timeout)
        else:
            if self.use_tcp_proto:
                self.local_station.start_iperf(serv_addr = dst_ip,
                                              test_udp = False,
                                              timeout = self.timeout)
            else: self._start_iperf(src_ip, dst_ip, self.tos_value)
        time.sleep(int(self.timeout))

        # Get mq statistics
        ad_linux_mqstat = tmethod.getStaMQStatistics(self.active_ap, self.ad_linux_mac, self.wlan_if)
        ad_linux_queue_info, ad_linux_empty_queues, ad_linux_empty_deq = tmethod.get_mqstatsInfo(ad_linux_mqstat, self.queue)

        # Verify MQ Statistics
        if self.port_matching:
            msg = "Verify that incoming traffic that matches with Port Match rule will be put "
            msg += "to the appropriate queue."
            logging.info(msg)
        if self.heuristics:
            logging.info("Verify that traffic will be put to the %s queue by heuristics" % self.queue)
        else:
            logging.info("Station %s on AP: verify that traffic will be inserted to the %s queue" %
                         (self.ad_linux_mac, self.queue))

        res, msg = tmethod.verifyMQStats(self.queue,
                                         ad_linux_queue_info,
                                         ad_linux_empty_queues,
                                         ad_linux_empty_deq,
                                         self.timeout,
                                         self.ad_linux_mac)
        if res == "FAIL":
            return [res, msg]

        # Verify ToS value of traffic at receiver
        if self.verify_tos:
            res, msg = tmethod.verifyToSValue(self.tcpdump_info,
                                              self.remote_linux_sta,
                                              src_ip, dst_ip,
                                              self.tos_value)
            if res == "FAIL": return res,msg
        else:
            if not self.use_tcp_proto:
                capture_res = tmethod.findCapturedPacket(self.remote_linux_sta, self.tcpdump_info,
                                                             src_ip, dst_ip)
                if not capture_res: return ["FAIL", "[Station %s]: does not receive traffic" % received_ip]

        return ["PASS", ""]

    def _getIntfNum(self, interface):
        pat_interface = "([0-9]+$)"
        num = -1
        inf_obj = re.search(pat_interface, interface)
        if inf_obj: num = int(inf_obj.group(1))
        else: raise Exception("Wrong interface name")

        return num
