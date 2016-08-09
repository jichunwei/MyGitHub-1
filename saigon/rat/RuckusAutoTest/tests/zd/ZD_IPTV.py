# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_IPTV class test IPTV feature for AP under Zone Director control

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
            'target_station':'ip address of target station',
            'wgs_cfg':'dictionary of wlan groups parameters',
            'wlan_cfg': 'dictionary of wlan groups parameters, if not provide, test will use default setting from tmethod8.get_default_wlan_cfg',
            'stream_server': 'IP address to test streaming traffic',

   Result type: PASS/FAIL
   Results: PASS: if traffic put in correct media queue.
            FAIL: if traffic put in incorrect media queue.

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
   2. Test:
        - Configure a WLAN and Wlan Group on AP
        - Assign Wlan Group to AP under test.
        - Streaming traffic with option base on parameter and verify traffic put to correct queue.
   3. Cleanup:
       - Remove all Wlan Groups created
       - Remove all Wlan created
"""

import os
import copy
import re
import logging
import time

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class ZD_IPTV(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_station'    : 'ip address of target station',
                           'wlan_group_cfg'    : 'dictionary of wlan groups parameters',
                           'wlan_cfg'          : 'dictionary of wlan groups parameters,\
                                                 if not provide, test will use default setting from tmethod8.get_default_wlan_cfg',
                           'stream_server'         : 'IP address to streaming traffic',
                           'media'             : 'name of a specific media ex: voice video data background',
                           'queue'             : 'name of media queue that traffic will come',
                           'tos_classify_value': 'value of tos configured for classification',
                           'tos_matching'      : 'This is the bool value determine if tos value when streaming traffic \
                                                 matches with the one configured in each queue or not',
                           'heuristics_enable' : 'This is bool value determine if heuristics is enabled or not.'}

    def config(self, conf):
        self.tc2f = {
            'heuristics': self._cfgClientToAssocWlan,
            'multicast': self._testToSStraffic,
            'unicast': self._testToSStraffic,
            'port_matching_filter': self._testPortMatchingFilter,
            'smartcast_streaming_downlink': self._testSmartCastStreamDownlink,
            'smartcast_max_igmp_groups': self._testSmartCastMaxIGMPGroups,
            'smartcast_igmp_join': self._testSmartCastIGMPJoin,
            'smartcast_igmp_leave': self._testSmartCastIGMPLeave
        }

        self._cfgInitTestParams(conf)
        self._cfgRemoveZDWlanGroupsAndWlan()
        self._cfgGetTargetStation()
        self._cfgGetActiveAP()
        self._removeQoSSettings()
        self.linux_server.kill_zing()
        lib.zd.ac.delete_all_l3_acl_policies(self.zd)
        if self.conf["combine_with_wispr_profile"]:
            self._cfgRemoveWISPrConfig()

        #@author: Jane.Guo @since: 2013-10
        self.conf['queue'] = lib.apcli.radiogrp.map_media_queue_info(self.active_ap,self.conf['queue'])

    def test(self):
        if self.conf["combine_with_wispr_profile"]:
            self._cfgDefineAuthSourceOnZD()
            self._cfgCreateHotspotProfileOnZD()
        self._cfgCreateWlanOnZD()
        self._cfgCreateWlanGroup()
        self._cfgAssignAPtoWlanGroup()
        self._cfgClientToAssocWlan()
        if self.errmsg: return ('FAIL', self.errmsg)
        self._get_clientWifiAddress()
        if self.errmsg: return ('FAIL', self.errmsg)
        if self.conf["combine_with_wispr_profile"]: self._cfgPerformHotspotAuthOnStation()
        if self.conf['acl_cfg']: self._cfgL4ACL()
        self.tc2f[self.conf['test_case']]()
        if self.errmsg: return ('FAIL', self.errmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        self.target_station.stop_iperf()
        self.target_station.delete_route(self.conf['stream_server'])
        server_interface = self.linux_server.get_interface_name_by_ip(self.linux_server.conf['ip_addr'])
        self.linux_server.delete_route(self.conf['stream_server'], self.conf['default_net_mask'], server_interface)
        lib.zd.ap.assign_to_default_wlan_group(self.zd, self.active_ap_mac)
        self._removeQoSSettings()
        #lib.zd.wgs.remove_wlan_groups(self.zd)
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        #if self.conf["combine_with_wispr_profile"]: self._cfgRemoveWISPrConfig()
        #lib.zd.ac.delete_all_l3_acl_policies(self.zd)

#
# config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout = 10,
                          check_status_timeout = 240,
                          check_wlan_timeout = 30,
                          break_time = 3,
                          num_of_pkts = '500',
                          default_net_mask = "255.255.255.255",
                          active_ap = '',
                          protocol = '',
                          queue = '',
                          filter_media = '',
                          filter_matching = '',
                          radio = '',
                          tos_classify_value = '',
                          tos_classify_enable = '',
                          tos_mark_enable = '',
                          tos_matching = '',
                          acl_cfg = '',
                          max_igmp_groups_file = '32_igmp_groups.pcap',
                          combine_with_wispr_profile = False
                          )
        self.conf.update(conf)

        if not self.conf.has_key('wlan_cfg'):
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg()
        if not self.conf.has_key('wlan_group_cfg'):
            self.conf['wlan_group_cfg'] = tmethod8.get_default_wlan_groups_cfg()

        self.wlan_cfg = self.conf['wlan_cfg']
        self.wlan_group_cfg = self.conf['wlan_group_cfg']
        default_ssid = self.conf['wlan_cfg']['ssid']
        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid(self.conf['wlan_cfg']['ssid'])
        if self.conf['combine_with_wispr_profile']:
            self.conf['wlan_cfg']['type'] = "hotspot"
        # update ssid in wlan group
        self.wlan_group_cfg['wlan_member'][self.conf['wlan_cfg']['ssid']] = self.wlan_group_cfg['wlan_member'][default_ssid].copy()
        del self.wlan_group_cfg['wlan_member'][default_ssid]

        self.zd = self.testbed.components['ZoneDirector']
        self.linux_server = self.testbed.components['LinuxServer']
        self.errmsg = ''
        self.passmsg = ''
        self.active_ap_mac = ''
        self.target_station = ''
        self.stream_server = self.conf['stream_server']

        # Heuristic values
        self.video_pktgap = ["0", "65"]
        self.video_pktlen = ["1000", "1518"]
        self.voice_pktgap = ["15", "275"]
        self.voice_pktlen = ["70", "400"]

        # default port and action for port filter matching rule
        self.conf['port'] = '5001'
        self.conf['action'] = 'tos'
        self.conf['dest_port'] = True

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        #logging.info("Remove all Wlan Groups on the Zone Director.")
        #lib.zd.wgs.remove_wlan_groups(self.zd, self.testbed.get_aps_sym_dict_as_mac_addr_list())
        #logging.info("Remove all WLAN on the Zone Director.")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

    def _cfgGetTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.conf['check_status_timeout']
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgGetActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in the test bed" % self.conf['active_ap'])

            self.active_ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['active_ap'])

    def _cfgCreateWlanOnZD(self):
        logging.info("Create WLAN [%s] as a standard WLAN on the Zone Director" % self.conf['wlan_cfg']['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.conf['wlan_cfg'])
        # make sure wlan_cfg['ssid'] is not belong to default wlanGroups
        # so we can isolate an AP to wlan_cfg['ssid'] -- to make 1Wlan 1AP possible
        lib.zd.wgs.uncheck_default_wlan_member(self.zd, self.wlan_cfg['ssid'])

    def _cfgRemoveWISPrConfig(self):
        logging.info("Remove all HOTSPOT profiles configured on the ZD")
        lib.zd.wispr.remove_all_profiles(self.zd)
        logging.info("Remove all AAA servers configured on the ZD")
        lib.zd.aaa.remove_all_servers(self.zd)


#
# test()
#
    def _cfgDefineAuthSourceOnZD(self):
        if self.conf['auth_info']['type'] == 'local':
            logging.info("Create a user account on the ZoneDirector")
            self.zd.create_user(self.conf['auth_info']['username'], self.conf['auth_info']['password'])
        else:
            logging.info("Create an authentication server on the ZoneDirector")
            server_info = {'server_addr': self.conf['auth_info']['svr_addr'],
                           'server_port': self.conf['auth_info']['svr_port'],
                           'server_name': self.conf['auth_info']['svr_name']}
            if self.conf['auth_info']['type'] == 'ad':
                server_info['win_domain_name'] = self.conf['auth_info']['svr_info']
            elif self.conf['auth_info']['type'] == 'ldap':
                server_info['ldap_search_base'] = self.conf['auth_info']['svr_info']
            elif self.conf['auth_info']['type'] == 'radius':
                server_info['radius_auth_secret'] = self.conf['auth_info']['svr_info']
            lib.zd.aaa.create_server(self.zd, **server_info)

        # Create radius accouting server if required
        if self.conf.has_key('acct_info'):
            logging.info("Create an accounting server on the ZoneDirector")
            server_info = {'server_addr': self.conf['acct_info']['svr_addr'],
                           'server_port': self.conf['acct_info']['svr_port'],
                           'server_name': self.conf['acct_info']['svr_name'],
                           'radius_acct_secret': self.conf['acct_info']['svr_info']}
            lib.zd.aaa.create_server(self.zd, **server_info)

    def _cfgCreateHotspotProfileOnZD(self):
        if self.conf.has_key('hotspot_cfg_list'):
            try:
                logging.info("Try to create %s Hotspot profiles" % self.conf['number_of_profile'])
                for cfg in self.conf['hotspot_cfg_list']:
                    logging.info("Create a Hotspot profile [%s] on the ZoneDirector" % cfg['name'])
                    lib.zd.wispr.create_profile(self.zd, **cfg)
                    time.sleep(2)
                self.msg += "%s Hotspot profiles have been created successfully. " % self.conf['number_of_profile']
            except:
                self.errmsg = "Unable to create %s Hotspot profiles" % self.conf['number_of_profile']
                return
            try:
                logging.info("Try to create one more Hotspot profile")
                cfg = copy.deepcopy(self.conf['hotspot_cfg'])
                cfg['name'] = "%s-extra" % cfg['name']
                lib.zd.wispr.create_profile(self.zd, **cfg)
                self.errmsg = "The ZD did allow creating more than %s Hotspot profiles" % self.conf['number_of_profile']
            except:
                self.msg += "The ZD didn't allow creating more than %s Hotspot profiles. " % self.conf['number_of_profile']
        else:
            logging.info("Create a Hotspot profile [%s] on the ZoneDirector" % self.conf['hotspot_cfg']['name'])
            lib.zd.wispr.create_profile(self.zd, **self.conf['hotspot_cfg'])

    def _cfgPerformHotspotAuthOnStation(self):
        logging.info("Perform Hotspot authentication on the station")
        if self.conf['hotspot_cfg'].has_key('start_page'):
            redirect_url = self.conf['hotspot_cfg']['start_page']

        else:
            redirect_url = ''

        arg = tconfig.get_hotspot_auth_params(
            self.zd, self.conf['auth_info']['username'],
            self.conf['auth_info']['password'],
            redirect_url = redirect_url
        )
        self.target_station.perform_hotspot_auth(arg)

        logging.info("Hotspot authentication was done on the station successfully. ")
        if self.conf['hotspot_cfg'].has_key('start_page'):
            logging.info("The station's Web session was redirected successfully to %s. " % self.conf['hotspot_cfg']['start_page'])


    def _cfgCreateWlanGroup(self):
        lib.zd.wgs.create_new_wlan_group(self.zd, self.wlan_group_cfg)

    def _cfgAssignAPtoWlanGroup(self):
        support_radio = lib.zd.ap.get_supported_radio(self.zd, self.active_ap_mac)
        for radio in support_radio:
            if radio == self.conf['radio']:
                lib.zd.ap.assign_to_wlan_group(self.zd, self.active_ap_mac , radio, self.wlan_group_cfg['name'])
        # wait for ZD put configuration to AP
        tmethod8.pause_test_for(10, "Wait for ZD put Wlan configuration to AP")

    def _cfgClientToAssocWlan(self):
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station,
                                                    self.wlan_cfg,
                                                    self.conf['check_status_timeout'])

    def _get_clientWifiAddress(self):
        (isOK, ip_addr, mac_addr) = tmethod.renew_wifi_ip_address(self.target_station,
                                                                self.conf['check_status_timeout'])
        if not isOK:
            self.errmsg = mac_addr
        else:
            self.wifi = dict(ip_addr = ip_addr, mac_addr = mac_addr)

    def _cfgL4ACL(self):
        logging.info("Create an L4 ACL")
        lib.zd.ac.create_l3_acl_policy(self.zd, self.conf['acl_cfg'])

    def _testHeuristicsAlgorithm(self):
        self.heuristics_info = self.active_ap.get_heuristics_cfg()
        # start Zing server on linux server
        self.linux_server.kill_zing()
        self.linux_server.start_zing_server()
        packet_gap = self.heuristics_info['packet_gap'][self.conf['queue']][1]
        self.wlan_inf = self.active_ap.ssid_to_wlan_if(self.wlan_cfg['ssid'])
        for packet_len in self.heuristics_info['packet_len'][self.conf['queue']]:
            logging.info("Clear mqstats statistic on active ap[%s]" % self.active_ap_mac)
            self.active_ap.clear_mqstats(self.wlan_inf)
            logging.info("Verify heuristics algorithm for video traffic with packet length[%s], packet gap [%s]" % (packet_len, packet_gap))
            self.target_station.send_zing(host = self.linux_server.ip_addr, delay = packet_gap, len_of_pkt = packet_len, num_of_pkts = self.conf['num_of_pkts'], udp = True)
            mqstats_table = self.active_ap.get_mqstats(self.wlan_inf)
            self._testMQStats(mqstats_table, self.conf['queue'])
            if self.errmsg:
                return
        self.passmsg = "Traffic is inserted to the %s queue correctly" % self.conf['queue']

    def _testMQStats(self, mqstats_table, right_queue):
        # get mqstats of active client
        mqstats = {}
        for mac_addr in mqstats_table.keys():
            if mac_addr.upper() == self.wifi['mac_addr'].upper():
                mqstats = mqstats_table[mac_addr][right_queue]
                break
        if not mqstats:
            self.errmsg = "Can't find MQstats for target_station[%s]" % self.wifi['mac_addr']
            return

        deq = int(mqstats['deq'])
        reenq = int(mqstats['reenq'])
        enq = int(mqstats['enq'])
        qued = int(mqstats['Qued'])

        if not deq:
            self.errmsg = "Station %s: queue %s is empty" % (self.wifi['mac_addr'], right_queue)
        elif (reenq + enq) != (deq + qued):
            self.errmsg = "Total packets of reenq and enq columns does not equal total packets of deq and qued columns"

    def _testToSStraffic(self):
        logging.info("Test multicast streaming traffic %s" % {True: "matched ToS value", False: ""}[self.conf['tos_matching']])
        self.wlan_inf = self.active_ap.ssid_to_wlan_if(self.wlan_cfg['ssid'])
        server_interface = self.linux_server.get_interface_name_by_ip(self.linux_server.conf['ip_addr'])

        if self.conf['test_case'] == 'multicast':
            logging.info("Add multicast route in routing table on wireless station and linux server")
            self.linux_server.add_route(self.conf['stream_server'], self.conf['default_net_mask'], server_interface)
            self.target_station.add_route(self.conf['stream_server'], self.conf['default_net_mask'], self.wifi['ip_addr'])

        # start capture packet on wireless station
        self.target_station.start_windump(self.wifi['ip_addr'])
        logging.info("Start iperf server on the wirless station [%s]" % self.wifi['ip_addr'])
        self.target_station.start_iperf(serv_addr = {'multicast':self.stream_server, 'unicast':""}[self.conf['test_case']], test_udp = True,
                                       multicast_srv = {'multicast':True, 'unicast':False}[self.conf['test_case']])

        logging.info("Clear media queue statistics on the active ap[%s]" % self.active_ap_mac)
        self.active_ap.clear_mqstats(self.wlan_inf)

        logging.info("Start %s streaming from linux server[%s] to station[%s]" % (self.conf['test_case'], server_interface,
                                                                                  self.wifi['ip_addr']))

        ##zj 2014-01-29 fixed ZF-7318   
        self.linux_server.start_iperf_client(stream_srv = self.wifi['ip_addr'] , test_udp = True, packet_len = "",
                                      timeout = "60", bw = "4m", tos = self.conf['tos_classify_value'])
        ##zj 2014-01-29 fixed ZF-7318  

        tmethod8.pause_test_for(30, "Wait for iperf streaming traffic")
        self.target_station.stop_windump()
        tmethod8.pause_test_for(3, "Wait for windump save packets to file")

        # verify test result
        mqstats_table = self.active_ap.get_mqstats(self.wlan_inf)
        self._testMQStats(mqstats_table, self.conf['queue'])
        if self.errmsg: return

        self._findCapturedPacket()
        if self.errmsg: return

        self.passmsg = "%s stream with %s matched ToS value work properly" % (self.conf['test_case'],
                                                                              {True: "", False:"no"}[self.conf['tos_matching']])

    def _testPortMatchingFilter(self):
        # start Zing server on linux server
        logging.info("Start zing server on the linux server")
        self.linux_server.start_zing_server()
        # configure ToS marking
        if self.conf['tos_mark_enable']:
            logging.info("Configure ToS marking value (%s) for %s queue" % (self.conf['tos_mark_value'], self.conf['media']))
            self.active_ap.set_tos_values(self.conf['media'], self.conf['tos_mark_value'])

        # Create a port matching filter on Active AP
        msg = "Add Port Matching Filter to the AP: proto ---> %s, port ---> %s, " % (self.conf['protocol'], self.conf['port'])
        msg += "action ---> %s, media ---> %s" % (self.conf['action'], self.conf['filter_media'])
        logging.info(msg)
        self.eth_interface = self.active_ap.get_eth_inferface_name()
        self.active_ap.add_port_matching_rule(self.eth_interface, self.conf['protocol'], self.conf['action'], self.conf['port'], self.conf['dest_port'],
                                           self.conf['filter_media'])

        self.wlan_inf = self.active_ap.ssid_to_wlan_if(self.wlan_cfg['ssid'])
        logging.info("Clear mqstats statistic on active ap[%s]" % self.active_ap_mac)
        self.active_ap.clear_mqstats(self.wlan_inf)

        if self.conf['tos_matching']:
            logging.info("Start Sniffer on wireless station")
            self.target_station.start_windump(self.wifi['ip_addr'])

        logging.info("Start to stream traffic from the station %s to the wireless station %s" %
                     (self.linux_server.ip_addr, self.wifi['ip_addr']))
        if self.conf['filter_media'] == 'voice':
            zing_pktgap = (int(self.voice_pktgap[0]) + 10) * 1000
            zing_pktlen = int(self.voice_pktlen[0]) + 10
        else:
            zing_pktgap = (int(self.video_pktgap[0]) + 10) * 1000
            zing_pktlen = int(self.video_pktlen[0]) + 10
        udp = {'udp':True, 'tcp': False}[self.conf['protocol']]
        self.target_station.send_zing(host = self.linux_server.ip_addr, delay = zing_pktgap, len_of_pkt = zing_pktlen,
                                     num_of_pkts = self.conf['num_of_pkts'], udp = udp)

        tmethod8.pause_test_for(30, "Wait for zing streaming %s traffic" % self.conf['protocol'])
        mqstats_table = self.active_ap.get_mqstats(self.wlan_inf)

        if self.conf['tos_matching']:
            self.target_station.stop_windump()
            tmethod8.pause_test_for(3, "Wait for windump save packets to file")

        self._testMQStats(mqstats_table, self.conf['queue'])
        if self.errmsg: return

        self._findCapturedPacket()
        if self.errmsg: return

        self.passmsg = "Port Matching Filter work with zing %s protocol%s" % (self.conf['protocol'],
                                                                              {True:" and ToS Marking", False:""}[self.conf['tos_mark_enable']])

    def _testSmartCastStreamDownlink(self):
        logging.info("Test multicast streaming traffic")
        self.wlan_inf = self.active_ap.ssid_to_wlan_if(self.wlan_cfg['ssid'])
        server_interface = self.linux_server.get_interface_name_by_ip(self.linux_server.conf['ip_addr'])

        logging.info("Add multicast route in routing table on wireless station and linux server")
        self.linux_server.add_route(self.conf['stream_server'], self.conf['default_net_mask'], server_interface)
        self.target_station.add_route(self.conf['stream_server'], self.conf['default_net_mask'], self.wifi['ip_addr'])

        # start capture packet on wireless station
        self.target_station.start_windump(self.wifi['ip_addr'])
        logging.info("Start iperf server on the wirless station [%s]" % self.wifi['ip_addr'])
        self.target_station.start_iperf(serv_addr = self.stream_server, test_udp = True, multicast_srv = True)

        logging.info("Clear media queue statistics on the active ap[%s]" % self.active_ap_mac)
        self.active_ap.clear_mqstats(self.wlan_inf)

        logging.info("Start %s streaming from linux server[%s] to station[%s]" % (self.conf['test_case'], server_interface,
                                                                                  self.wifi['ip_addr']))
        self.linux_server.start_iperf_client(stream_srv = self.stream_server , test_udp = True, packet_len = "",
                                      timeout = "60", bw = "4m", tos = self.conf['tos_classify_value'])

        tmethod8.pause_test_for(30, "Wait for iperf streaming traffic")
        self.target_station.stop_windump()
        tmethod8.pause_test_for(3, "Wait for windump save packets to file")

        # verify test result
        mqstats_table = self.active_ap.get_mqstats(self.wlan_inf)
        self._testMQStats(mqstats_table, self.conf['queue'])
        if self.errmsg: return

        self._findCapturedPacket()
        if self.errmsg: return

        self.passmsg = "Streaming downlink from Server behind ZD to station work properly"

    def _testSmartCastMaxIGMPGroups(self):
        logging.info("Reboot AP to clear IGMP table entry")
        self.active_ap.reboot()
        tmethod8.pause_test_for(60, "Wait for AP reboot and re-join Zone Director")

        logging.info("Start sending 32 IGMP groups to active AP [%s]" % self.active_ap_mac)
        server_interface = self.linux_server.get_interface_name_by_ip(self.linux_server.conf['ip_addr'])
        self.linux_server.start_tcp_replay(server_interface, self.conf['max_igmp_groups_file'])

        logging.info("Verify that AP can create 32 IGMP groups")
        gblQoS_content = self.active_ap.get_gblqos()
        self._testMaxIGMPGroups(gblQoS_content)

        if not self.errmsg:
            self.passmsg = "AP can create maximum 32 IGMP groups in IGMP table"

    def _testSmartCastIGMPJoin(self):
        logging.info("Test multicast streaming traffic")
        self.wlan_inf = self.active_ap.ssid_to_wlan_if(self.wlan_cfg['ssid'])
        server_interface = self.linux_server.get_interface_name_by_ip(self.linux_server.conf['ip_addr'])

        logging.info("Add multicast route in routing table on wireless station and linux server")
        self.linux_server.add_route(self.conf['stream_server'], self.conf['default_net_mask'], server_interface)
        self.target_station.add_route(self.conf['stream_server'], self.conf['default_net_mask'], self.wifi['ip_addr'])

        logging.info("Start iperf server on the wirless station [%s]" % self.wifi['ip_addr'])
        self.target_station.start_iperf(serv_addr = self.stream_server, test_udp = True, multicast_srv = True)

        logging.info("Geting IGMP table")
        gblQoS_content = self.active_ap.get_gblqos()
        self._findIGMPUpdateMsg(self.stream_server, "STA Join", gblQoS_content)
        self.passmsg = "IGMP join work properly"

    def _testSmartCastIGMPLeave(self):
        logging.info("Test multicast streaming traffic")
        self.wlan_inf = self.active_ap.ssid_to_wlan_if(self.wlan_cfg['ssid'])
        server_interface = self.linux_server.get_interface_name_by_ip(self.linux_server.conf['ip_addr'])

        logging.info("Add multicast route in routing table on wireless station and linux server")
        self.linux_server.add_route(self.conf['stream_server'], self.conf['default_net_mask'], server_interface)
        self.target_station.add_route(self.conf['stream_server'], self.conf['default_net_mask'], self.wifi['ip_addr'])

        logging.info("Start iperf server on the wirless station [%s]" % self.wifi['ip_addr'])
        self.target_station.start_iperf(serv_addr = self.stream_server, test_udp = True, multicast_srv = True)

        logging.info("Stop iperf server on the wireless station [%s])" % self.wifi['ip_addr'])
        self.target_station.stop_iperf()

        logging.info("Geting IGMP table")
        gblQoS_content = self.active_ap.get_gblqos()
        self._findIGMPUpdateMsg(self.stream_server, "Leave Msg", gblQoS_content)
        self.passmsg = "IGMP join work properly"


    def _testMaxIGMPGroups(self, gblQoS_content):
        # Generate IGMP groups list like igmp groups in max_igmp_groups file
        # to verify igmp create correctly in /proc/media/gblQoS correctly
        igmp_groups_list = ["239.255.0.%s" % i for i in range(2, 34)]
        igmp_groups_not_found_list = []
        for igmp_group in igmp_groups_list:
            found = False
            for entry in gblQoS_content:
                if igmp_group in entry: found = True
            if not found: igmp_groups_not_found_list.append(igmp_group)

        if igmp_groups_not_found_list and len(gblQoS_content) < 32:
            self.errmsg = "Fail to create maximum 32 IGMP groups: %s" % igmp_groups_not_found_list
            logging.debug("These IGMP groups wasn't created in IGMP table: %s" % igmp_groups_not_found_list)

    def _findCapturedPacket(self):
        captured_traffic = eval(self.target_station.parse_traffic())
        for packet in captured_traffic:
            try:
                if packet.has_key('dst_ip'):
                    if (packet['dst_ip'] == self.stream_server and packet['tos'].upper() != self.conf['tos_classify_value'].upper() and
                        self.conf['tos_matching']):
                        self.errmsg = "AP sent packets with incorrect ToS value [%s]" % packet['tos']
                        break
            except Exception, e:
                logging.debug(packet)
                logging.debug(e.message)

    def _findIGMPUpdateMsg(self, igmp_group, msg, gblQoS_content):
        found = False
        for entry in gblQoS_content:
            if igmp_group in entry:
                if msg in entry: found = True

        if not found:
            self.errmsg = "IGMP group [%s] with status %s is not in IGMP table" % (igmp_group, msg)
#
# cleanup()
#

    def _removeQoSSettings(self):
        eth_interface = self.active_ap.get_eth_inferface_name()
        if self.conf['test_case'] == 'port_matching_filter':
            logging.info("Remove port matching filter")
            self.active_ap.remove_port_matching_rule(eth_interface)

