# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: IPTV_Unicast_Streaming class tests ability of queuing traffic when streaming with the given conditions.
    Author: Tam Nguyen
    Prerequisite (Assumptions about the state of the testbed/DeviceUnderTest):

    1. Build under test is loaded on the AP
    Required components: RuckusAP, StationLinuxPC
    Test parameters: {'active_ap': 'ip address of active ap',
                      'remote_station': 'ip address of remote linux pc',
                      'local_station': 'ip address of local linux pc',
                      'active_ad': 'ip address of active adapter',
                      'media': 'name of a specific media, ex: voice, video, data, background',
                      'queue': 'name of media queue that traffic will come',
                      'tos_classify_value': 'value of tos configured for classification',
                      'tos_mark_value': 'value of tos configured for marking',
                      'tos_matching':'This is the bool value determine if tos value when streaming traffic matches
                                      with the one configured in each queue or not',
                      'tos_classify_enable': 'This is the bool value determine if ToS classification is enabled or not',
                      'tos_mark_enable': 'This is the bool value determine if ToS Marking is enabled or not.',
                      'heuristics_enable': 'This is bool value determine if heuristics is enabled or not.'}

    Result type: PASS/FAIL

    Results: PASS: Verify that when streaming traffic with matching ToS value and ToS classification enabled,
                    traffic will be put to the appropriate queue. Otherwise, traffic will be queued by heuristics.
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
        - If tos_classify_enable is True:
            + Enable ToS classification on the specific interface
            + If streaming traffic with no ToS value, verify that traffic will be queued by heuristics
            + If streaming traffic with matching ToS value of voice queue:
                + Configure ToS Classify value for voice queue
                + Verify that that traffic will be put to the voice queue correctly
            + If streaming traffic with matching ToS value of video queue:
                + Configure ToS classify value for video queue
                + Verify that traffic will be put to the video queue correctly
            + If streaming traffic with non-matching ToS value, verify that traffic will be queued by heuristics
            + If streaming traffic when ToS marking enabled with filter rule for voice:
                + Configure ToS marking value for voice queue
                + Add Port Matching Filter to the AP for voice traffic with following information:
                destination port is Iperf server's port, proto is UDP, action is tos.
                + Verify that when streaming traffic that matching this filter rule, outgoing traffic will be marked
                by voice ToS value.
            + If streaming traffic when ToS marking enabled with filter rule for video:
                + Configure ToS marking value for video queue
                + Add Port Matching Filter to the AP for video traffic with following information:
                destination port is Iperf server's port, proto is UDP, action is tos.
                + Verify that when streaming traffic matching this filter rule, outgoing traffic will be marked
                by video ToS value.
        - If tos_classify_enable is False:
            + Disable ToS Classification on the specific interface
            + Verify that when streaming traffic, even traffic with matching ToS value,
            traffic will be queued by heurictics.
        - If heuristics disabled, verify that traffic will be put to the Data queue

    3. Cleanup:
        - Return the previous QoS configuration for the AP
        - Down svcp interface on the AP and adapter

    How is it tested:
        - Before streaming traffic with matching voice ToS value, login to AP CLI and change ToS value of voice
        to another one, the script should return FAIL and report that voice queue is empty
        - Before streaming traffic with matching video ToS value, login to AP CLI and change ToS value of video
        to another one, the script should return FAIL and report that video queue is empty
"""

import time
import logging
import tempfile
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.common.Ratutils import *
from libIPTV_TestConfig import *
from libIPTV_TestMethods import *

class IPTV_Unicast_Streaming(Test):
    required_components = ['RuckusAP', 'StationLinuxPC']
    parameter_description = {'active_ap': 'ip address of active ap',
                             'remote_station': 'ip address of remote linux pc',
                             'local_station': 'ip address of local linux pc',
                             'active_ad': 'ip address of active adapter',
                             'ap_channel':'channel of AP/Adapter',
                             'media': 'name of a specific media, ex: voice, video, data, background',
                             'queue': 'name of media queue that traffic will come',
                             'tos_classify_value': 'value of tos configured for classification',
                             'tos_mark_value': 'value of tos configured for marking',
                             'tos_matching':'This is the bool value determine if tos value when streaming traffic matches \
                                            with the one configured in each queue or not',
                             'tos_classify_enable': 'This is the bool value determine \
                                                if ToS classification is enabled or not',
                             'tos_mark_enable': 'This is the bool value determine if ToS Marking is enabled or not.',
                             'heuristics_enable': 'This is bool value determine if heuristics is enabled or not.'}

    def config(self, conf):

        logging.info('Test config: %s' % pformat(conf))
        self._getQoSTestParams(conf)
        self._defineTestParams(conf)
        self._getStations(conf)

        self.ap_ip_addr = self.testbed.getAPIpAddrBySymName(conf['active_ap'])
        self.ad_ip_addr = self.testbed.getAdIpAddrBySymName(conf['active_ad'])

        logging.info("Find the active AP object")
        self.active_ap = getTestbedActiveAP(self.testbed, conf['active_ap'],
                                            self.testbed.components['AP'],
                                            self.ap_channel, self.wlan_if)

        logging.info("Get active adapter configuration information")
        self.ad_config = getADConfig(self.testbed, conf['active_ad'], self.testbed.ad_list)

        self.eth_interface = self.active_ap.get_eth_inferface_name()
        self._saveConfig()
        self.ad_mac = self.remote_station.get_ad_wireless_mac(self.ad_config)
        self.ad_model = self.remote_station.get_ad_device_type(self.ad_config)

    def test(self):
        wlan_cfg = dict(auth="open",
                        encryption="none",
                        ssid='IPTV_%s' % self.wlan_if,
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

        # Get BSSID to support capturing packets over the air
        self.bssid = getBSSID(self.active_ap, self.wlan_if)

        # Change configuration on wlan interface
        self.capture_station.cfg_wlan_if(ip_addr = self.wireless_interface_ip_addr, channel = self.ap_channel)

        if self.heuristics_enable:
            self.active_ap.set_heuristics_status("enable", self.eth_interface)
            if self.tos_classify_enable:
                # Enable ToS classification on the active AP
                self.active_ap.set_tos_classification(self.eth_interface, True)

                # If streamed traffic has ToS value that is the same as the one configured in any media queue
                if self.tos_matching:
                    logging.info("Configure ToS classify value (%s) for %s queue" %
                                 (self.tos_classify_value, self.media))
                    self.active_ap.set_tos_values(self.media, self.tos_classify_value)

                # If ToS marking enabled
                if not self.tos_classify_value and self.tos_mark_enable:
                    if not self.build_stream:
                        self.active_ap.set_tos_marking(self.eth_interface, True)

                    logging.info("Configure ToS marking value (%s) for %s queue" % (self.tos_mark_value, self.media))
                    self.active_ap.set_tos_values(self.media, self.tos_mark_value, False)

                if self.filter_matching:
                    msg = "Add Port Matching Filter to the AP: proto ---> %s, port ---> %s, " % (self.proto, self.port)
                    msg += "action ---> %s, media ---> %s" % (self.action, self.filter_media)
                    logging.info(msg)
                    self.active_ap.add_port_matching_rule(self.eth_interface, self.proto, self.action,
                                                       self.port, self.dest_port, self.filter_media)

                if self.heuristics_matching:
                    logging.info("Configure parameters for heuristics algorithm: ")
                    if self.heuristics_media == 'voice':
                        logging.info("Packet length ----> %s, packet gap ----> %s" % (self.voice_pktlen, self.voice_pktgap))
                        self.active_ap.set_heuristics_cfg(self.heuristics_media,
                                                           cfg_pktgap = True,
                                                           min_value = self.voice_pktgap[0],
                                                           max_value = self.voice_pktgap[1])
                        self.active_ap.set_heuristics_cfg(self.heuristics_media,
                                                           cfg_pktlen = True,
                                                           min_value = self.voice_pktlen[0],
                                                           max_value = self.voice_pktlen[1])
                    else:
                        logging.info("Packet length ----> %s, packet gap ----> %s" % (self.video_pktlen, self.video_pktgap))
                        self.active_ap.set_heuristics_cfg(self.heuristics_media,
                                                           cfg_pktgap = True,
                                                           min_value = self.video_pktgap[0],
                                                           max_value = self.video_pktgap[1])
                        self.active_ap.set_heuristics_cfg(self.heuristics_media,
                                                           cfg_pktlen = True,
                                                           min_value = self.video_pktlen[0],
                                                           max_value = self.video_pktlen[1])
            else:
                # Disable ToS classification on the active AP
                self.active_ap.set_tos_classification(self.eth_interface, False)
                if self.tos_matching:
                    self.active_ap.set_tos_values(self.media, self.tos_classify_value)
        else:
            logging.info("Disable Heuristics")
            self.active_ap.set_heuristics_status("disable", self.eth_interface)

            # Enable ToS classification on the active AP
            self.active_ap.set_tos_classification(self.eth_interface, True)
            if self.tos_matching:
                logging.info("Configure ToS classify value (%s) for %s queue" % (self.tos_classify_value, self.media))
                self.active_ap.set_tos_values(self.media, self.tos_classify_value)

        res, msg = self._streamTraffic()
        if res == "FAIL":
            return [res, msg]

        return ["PASS", ""]

    def cleanup(self):

        if self.active_ap:
            logging.info("Return the previous encryption for AP")
            self.active_ap.cfg_wlan(self.current_ap_encryption)

            logging.info("Return the previous status of ToS classification")
            self.active_ap.set_tos_classification(self.eth_interface, self.cur_tos_classify_status)

            if self.tos_matching:
                logging.info("Return the previous ToS value for %s" % self.media)
                self.active_ap.set_tos_values(self.media, self.cur_tos_classify_value)

            if self.tos_mark_enable:
                if not self.build_stream:
                    logging.info("Return the previous status of ToS marking")
                    self.active_ap.set_tos_marking(self.eth_interface, self.cur_tos_mark_status)

                logging.info("Return the previous ToS marking value for %s" % self.media)
                self.active_ap.set_tos_values(self.media, self.cur_tos_mark_value, False)

            if self.filter_matching:
                if self.cur_port_match_status:
                    logging.info("Return the previous status of Port matching filter")
                    self.active_ap.set_port_match_status(self.cur_port_match_status, self.eth_interface)

                logging.info("Remove port matching filter")
                self.active_ap.remove_port_matching_rule(self.eth_interface)

            if not self.heuristics_enable:
                logging.info("Enable heuristics on the active AP")
                self.active_ap.set_heuristics_status("enable", self.eth_interface)

            if self.heuristics_matching:
                logging.info("Return the previous configuration for heuristics")
                pkg_min = self.heuristics_info['packet_gap'][self.heuristics_media][0]
                pkg_max = self.heuristics_info['packet_gap'][self.heuristics_media][1]
                pklen_min = self.heuristics_info['packet_len'][self.heuristics_media][0]
                pklen_max = self.heuristics_info['packet_len'][self.heuristics_media][1]

                self.active_ap.set_heuristics_cfg(self.heuristics_media,
                                                   cfg_pktlen = True,
                                                   min_value = pklen_min,
                                                   max_value = pklen_max)

                self.active_ap.set_heuristics_cfg(self.heuristics_media,
                                                   cfg_pktgap = True,
                                                   min_value = pkg_min,
                                                   max_value = pkg_max)

            logging.info("Down %s interface on the active AP" % self.wlan_if)
            self.active_ap.set_state(self.wlan_if, 'down')
            time.sleep(2)

        if self.remote_station and self.local_station:
            if not self.heuristics_matching:
                logging.info("Kill iperf server process on the remote station %s" % self.remote_sta_ip_addr)
                self.remote_station.stop_iperf()
            else:
                logging.info("Kill zing server process on the local station %s" % self.local_sta_ip_addr)
                self.local_station.stop_zing()

            logging.info("Down svcp interface on the active Adapter")
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
            else:
                verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_sta_ip_addr, 5000, False)
        logging.info("---------- FINISH ----------")

    def _streamTraffic(self):

        for bw in self.bw_list:
            # Send some learning packet
            verifyStaConnection(self.local_station, self.local_sta_ip_addr, self.remote_sta_ip_addr)
            if not self.heuristics_matching:
                logging.info("Stream traffic with bandwidth %sbps" % bw.upper())
                logging.info("Start iperf server on the station %s" % self.remote_sta_ip_addr)
                self.remote_station.start_iperf(test_udp = True)

            else:
                logging.info("Start zing server on the local station %s" % self.local_sta_ip_addr)
                self.local_station.start_zing(test_udp = True, tos = self.tos_classify_value)

            # Capture traffic on the remote station to verify ToS value
            if self.tos_classify_value or self.tos_mark_enable:
                fo, tcpdump_info_file = tempfile.mkstemp(".txt")
                logging.info("Use tool tcpdump to capture traffic on the remote station %s" % self.remote_sta_ip_addr)
                self.remote_station.start_tcp_dump(ip_addr = self.remote_sta_ip_addr,
                                                 proto = "udp", count = "40",
                                                 file_path = tcpdump_info_file)

            logging.info("Clear media queue statistics on the active ap")
            self.active_ap.clear_mqstats(self.wlan_if)
            time.sleep(1)

            if not self.heuristics_matching:
                logging.info("Start to stream traffic from the station %s to the remote station %s" %
                             (self.local_sta_ip_addr, self.remote_sta_ip_addr))
                self.local_station.start_iperf(serv_addr = self.remote_sta_ip_addr,
                                              test_udp = True,
                                              packet_len = self.packet_len,
                                              timeout = self.timeout,
                                              bw = bw, tos = self.tos_classify_value)
            else:
                logging.info("Start to stream traffic from the station %s to the remote station %s" %
                             (self.local_sta_ip_addr, self.remote_sta_ip_addr))
                if self.heuristics_media == "voice":
                    zing_pktgap = (int(self.voice_pktgap[0]) + 10) * 1000
                    zing_pktlen = int(self.voice_pktlen[0]) + 10
                else:
                    zing_pktgap = (int(self.video_pktgap[0]) + 10) * 1000
                    zing_pktlen = int(self.video_pktlen[0]) + 10
                self.remote_station.start_zing(server_addr = self.local_sta_ip_addr,
                                              pkt_gap = zing_pktgap,
                                              pkt_len = zing_pktlen,
                                              test_udp = True,
                                              timeout = self.timeout)

#            # Capture traffic over the air
            time.sleep(10)
            if self.ad_model.lower() != 'vf7111':
                fd, tshark_info_file = tempfile.mkstemp(".txt")
                logging.info("Use tshark to capture traffic over the air")
                self.capture_station.capture_traffic_ota(ip_addr = self.wireless_interface_ip_addr,
                                                       filename = tshark_info_file,
                                                      expression = "ether host",
                                                      host = self.bssid, count = "2000")
            time.sleep(int(self.timeout) - 5)

            mq_statistics = getStaMQStatistics(self.active_ap, self.ad_mac, self.wlan_if)
            # If traffic is queued by heuristics.
            # Get heuristics configuration to check exact queue that traffic will come
            if not self.queue:
                match_length_voice = False
                match_length_video = False

                length = self.active_ap.get_heuristics_cfg()['packet_len']
                # Verify packet length configured for heuristics
                for key in length.keys():
                    if key == 'voice':
                        if int(length[key][0]) <= self.packet_len and int(length[key][1]) >= self.packet_len:
                            match_length_voice = True
                    else:
                        if int(length[key][0]) <= self.packet_len and int(length[key][1]) >= self.packet_len:
                            match_length_video = True

                if match_length_video:
                    self.queue = "video"
                elif match_length_voice:
                    self.queue = "voice"
                else:
                    self.queue = "data"

            # Get traffic information on each queue
            right_queue_info, empty_queues, empty_deq = get_mqstatsInfo(mq_statistics, self.queue)

            # Define logging message
            if self.heuristics_enable:
                if self.tos_classify_enable:
                    if not self.tos_classify_value:
                        if self.tos_mark_enable:
                            msg = "Verify that incoming traffic that matches with Port Match rule will be put "
                            msg += "to the appropriate queue. ToS value of outgoing traffic will be marked"
                            logging.info(msg)
                    else:
                        if not self.tos_matching:
                            logging.info("Verify that traffic will be put to the %s queue by heuristics" % self.queue)
                        else:
                            logging.info("Verify that traffic will be put to the %s queue because of matching %s ToS value" %
                                         (self.queue, self.media))
                else:
                    logging.info("Length of sent packets: %s" % self.packet_len)
                    logging.info("Packet length configured by heuristics: voice ----> %s, video ----> %s" %
                                 (length['voice'], length['video']))
                    logging.info("Verify that traffic will be put to the %s queue by heuristics" % self.queue)
            else:
                if self.tos_matching:
                    logging.info("Verify that traffic will be put to the %s queue althougth heuristics is disabled" %
                                 self.queue)
                else:
                    logging.info("Verify that traffic will be put to the data queue")

            # Verify MQ statistics
            res, msg = verifyMQStats(self.queue, right_queue_info, empty_queues, empty_deq, self.timeout, self.ad_mac)
            if res == "FAIL":
                return [res, msg]

            # Verify ToS value of traffic at receiver
            if self.tos_classify_value:
                res, msg = verifyToSValue(tcpdump_info_file, self.remote_station, self.local_sta_ip_addr,
                                          self.remote_sta_ip_addr, self.tos_classify_value)
                if res == "FAIL": return [res, msg]
            else:
                if self.tos_mark_enable:
                    res, msg = verifyToSValue(tcpdump_info_file, self.remote_station,
                                              self.local_sta_ip_addr, self.remote_sta_ip_addr,
                                              self.tos_mark_value, True)
                    if res == "FAIL": return [res, msg]
            time.sleep(2)
            # Analyze traffic over the air
            if self.ad_model.lower() != 'vf7111':
                res, msg = analyzeTrafficOTA(tshark_info_file, self.capture_station,
                                             self.local_sta_ip_addr,
                                             self.remote_sta_ip_addr, self.queue)

                if res == "FAIL": return [res, msg]

        return ["PASS", ""]

    def _getQoSTestParams(self, conf):

        self.use_pppoe = conf['use_pppoe']
        if conf.has_key('tos_classify_value'):
            self.tos_classify_value = conf['tos_classify_value']
        else:
            self.tos_classify_value = ""

        if conf.has_key('tos_mark_value'): self.tos_mark_value = conf['tos_mark_value']
        else: self.tos_mark_value = ""

        if conf.has_key('tos_matching'): self.tos_matching = conf['tos_matching']
        else: self.tos_matching = False

        if conf.has_key('media'): self.media = conf['media']
        else: self.media = ""

        if conf.has_key('tos_mark_enable'):
            self.tos_mark_enable = conf['tos_mark_enable']
        else: self.tos_mark_enable = False

        if conf.has_key('queue'): self.queue = conf['queue']
        else: self.queue = ""

        if conf.has_key('heuristics_matching'):
            self.heuristics_matching = conf['heuristics_matching']
        else: self.heuristics_matching = False

        if conf.has_key('heuristics_media'): self.heuristics_media = conf['heuristics_media']
        else: self.heuristics_media = ""

        if conf.has_key('filter_media'): self.filter_media = conf['filter_media']
        else: self.filter_media = self.media

        if conf.has_key('filter_matching'): self.filter_matching = conf['filter_matching']
        else: self.filter_matching = False

        self.heuristics_enable = conf['heuristics_enable']
        self.tos_classify_enable = conf['tos_classify_enable']
        self.wlan_if = conf['wlan_if']

        if conf.has_key('build_stream'): self.build_stream = conf['build_stream']
        else: self.build_stream = True

    def _getStations(self, conf):
        # Find exactly stations
        station_list = self.testbed.components['Station']
        self.remote_station = getStation(conf['remote_station'], station_list)
        self.local_station = getStation(conf['local_station'], station_list)
        self.capture_station = getStation(conf['capture_station'], station_list)

    def _defineTestParams(self, conf):

        self.proto = "udp"
        self.action = "tos"
        self.port = "5001"
        self.dest_port = True

        # Iperf parameters
        self.timeout = "60"
        self.packet_len = '800'

        self.remote_station = None
        self.local_station = None
        self.active_ap = None
        self.ad_config = {}
        self.ap_channel = conf['ap_channel']

        # Heuristics values
        self.video_pktgap = ['5', '85']
        self.video_pktlen = ['900', '1500']
        self.voice_pktgap = ['30', '200']
        self.voice_pktlen = ['60', '500']

        self.bw_list = ['4m']

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

        self.wireless_interface_ip_addr = getLinuxIpAddr(self.capture_station, self.testbed.sta_wireless_interface_info)
        if not self.wireless_interface_ip_addr:
            raise Exception("IP address of wireless interface on the linux station %s is not correct" %
                            self.remote_sta_ip_addr)

    def _saveConfig(self):
        logging.info("Save encryption information")
        self.current_ap_encryption = self.active_ap.get_encryption(self.wlan_if)
        self.current_ap_encryption['wlan_if'] = self.wlan_if

        self.current_ad_encryption = self.remote_station.get_ad_encryption(self.ad_config, 'wlan0')
        self.current_ad_encryption['wlan_if'] = 'wlan0'

        logging.info("Save current QoS configuration on the active AP")
        self.cur_tos_classify_status = self.active_ap.get_tos_classification(self.eth_interface)
        if not self.build_stream:
            self.cur_tos_mark_status = self.active_ap.get_tos_marking(self.eth_interface)
        if self.tos_matching:
            self.cur_tos_classify_value = saveToSValues(self.active_ap, self.media)

        if self.tos_mark_enable:
            # Save current ToS value for marking on the active AP
            res = self.active_ap.get_tos_values(False)
            for key in res.keys():
                if key.lower().startswith('voip'): temp = 'voice'
                else: temp = key.lower()

                if temp == self.media:
                    self.cur_tos_mark_value = res[key]
                    break

        # Save current port match status on the active AP
        if self.filter_matching:
            self.cur_port_match_status = saveCurPortMatchingFilterStatus(self.active_ap, self.eth_interface)
        # Save the current configuration of heuristics algorithm on the active AP
        if self.heuristics_matching:
            self.heuristics_info = self.active_ap.get_heuristics_cfg()
