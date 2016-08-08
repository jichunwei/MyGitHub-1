# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_EncryptionTypesWebAuth Test class tests the ability of a station to associate with
             an AP under ZD's control with a given security configuration,
             vlan enabled and Web authentication mechanism. The ability to associate is confirmed via a ping test.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'ip': 'IP address to ping. Should be given in format n.n.n.n/m.m.m.m',
                    'target_station': 'IP address of target station',
                    'active_ap': 'MAC address of target ap, optional',
                    'wlan_cfg': 'dictionary of security settings, optional',
                    'connection_mode': 'l2/l3, optional',
                    'enable_tunnel': 'True/False, optional',
                    'ap_model': 'AP model, optional',
                    'expected_subnet': 'used to validate the leased IP address of wireless client, optional',
                    'vlan_id': 'VLAN ID assigned to the WLAN'

   Result type: PASS/FAIL
   Results: PASS: target station can associate, pass WebAuth, ping to a destination successfully and
                  information is shown correctly in ZD and AP
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
       - Get list of connected APs and find the active AP
   2. Test:
       - Configure a WLAN on the ZD with given security setting and vlan enabled if the parameter 'vlan_id' is passed.
       - If the parameter 'ip active' is passed,
         go to the non-active AP and remove all the WLAN configuration that it receives from the ZD.

       - If the parameter 'ip active' is passed, on the active AP, verify if the BSSID is generated correctly.
       - Configure the target station with given security setting
       - Wait until it gets associated and get correct IP and MAC addresses of the wireless adapter
       - Do a ping to make sure the AP doesn't forward the traffic from the station
       - Verify if the ZD shows correct information about the connected station
       - Do Web authentication from the station
       - Do a ping again to make sure traffic gets forwarded
       - Verify ZD and AP again if they show correct information about the connected station
   3. Cleanup:
       - Remove all wlan configuration on ZD
       - Remove wireless profile on remote wireless STA
       - Verify if wireless station is completed disconnect after remove wireless profile.

   How it is tested?
       - While the test is running, right after the user is created on the ZD (or on the authentication servers),
         go to the User configuration page and remove the user (or go to the server and remove it). The script
         should report that it is unable to do the Web authentication on the remote station
       - After the client has done the authentication successfully, go to the table Active Clients and delete that
         user. The script should report that the ZD has incorrect info about the client
"""

import os
import re
import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import Ratutils as utils
# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_EncryptionTypesWebAuth_WlanGroups(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'ip': 'IP address to ping. Should be given in format n.n.n.n/m.m.m.m',
                           'target_station': 'IP address of target station',
                           'active_ap': 'MAC address of target ap, optional',
                           'wlan_cfg': 'dictionary of security settings, optional',
                           'connection_mode': 'l2/l3, optional',
                           'enable_tunnel': 'True/False, optional',
                           'expected_subnet': 'used to validate the leased IP address of wireless client, optional',
                           'vlan_id': 'VLAN ID assigned to the WLAN'}
    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgGetTargetStation()
        self._cfgRemoveZDWlanGroupsAndWlan()
        self._cfgGetActiveAP()
        self._cfgCleanupSwitchMacTable()

    def test(self):
        self._cfg_wlanForAP()
        self._isolateAPWithWlanGroups()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testWlanIsUp()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._cfgCreateAuthenticationMethod()
        self._configClientToAssocWlan()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._get_clientWifiAddress()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testIfVlanCheckClientAndDestAtSameSubnet()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testClientShouldNotReachDest()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyZDClientIsUnauthorized()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._cfgStationPerformWebAuth()

        # always check Client is Authorized, but ignore its outcome
        self._testVerifyZDClientIsAuthorized()

        self._testClientAllowToReachDest()
        if self.errmsg: return ('FAIL', self.errmsg)

        # OK; if it is pingable; but client is not authorized; problem
        self._testVerifyZDClientIsAuthorized()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyClientAssocProperly(self.client_info)
        if self.errmsg: return ('FAIL', self.errmsg)

        # Verify information of the target station shown on the AP if the parameter 'active_ap' is passed.
        self._testClientIsAtActiveAP(self.client_info)
        if self.errmsg: return ("FAIL", self.errmsg)

        # Verify the wireless client's MAC address to see if it is on ZD side or AP side
        self._testStationMacInTunnelMode()
        if self.errmsg: return ("FAIL", self.errmsg)

        msg = "ActiveAP[%s %s %s %s] can support WebAuth with Auth[%s] Encryption[%s] " \
            % (self.conf['active_ap'], self.active_ap.get_ap_model(),
                self.active_ap.base_mac_addr, self.active_ap.ip_addr,
                self.wlan_cfg['auth'], self.wlan_cfg['encryption'])
        return ('PASS', msg)

    def cleanup(self):
        #self._cfgRemoveZDWlanGroupsAndWlan()
        self._cfgDeleteStationFromZD()

    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout = 10,
                          check_status_timeout = 240,
                          check_wlan_timeout = 30,
                          break_time = 3,
                          radio_mode = '')
        self.conf.update(conf)
        if not self.conf.has_key('wlan_cfg'):
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg(self.conf['vlan_id'])
        if not self.conf.has_key('wgs_cfg'):
            self.conf['wgs_cfg'] = tmethod8.get_default_wlan_groups_cfg(self.conf['radio_mode'])
        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid(self.conf['wlan_cfg']['ssid'])
        self.wlan_cfg = self.conf['wlan_cfg']
        self.wlan_cfg['use_web_auth'] = True
        self.wgs_cfg = self.conf['wgs_cfg']
        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        #self.gateway_ip = self.conf['dest_ip'] if self.conf.has_key('dest_ip') else self.conf['ip']

        tmp_list = self.conf['dest_ip'].split("/")
        self.test_ip_addr = tmp_list[0]
        if len(tmp_list) == 2:
            self.expected_subnet_mask = tmp_list[1]
        else:
            self.expected_subnet_mask = ""

        if self.conf.has_key('vlan_id'):
            self.wlan_cfg['vlan_id'] = self.conf['vlan_id']

        if self.conf.has_key('connection_mode'):
            self.connection_mode = self.conf['connection_mode']
        else:
            self.connection_mode = ""

        if self.conf.has_key('enable_tunnel'):
            self.wlan_cfg['do_tunnel'] = self.conf['enable_tunnel']
        else:
            self.wlan_cfg['do_tunnel'] = False

        if self.conf.has_key('expected_subnet'):
            l = self.conf['expected_subnet'].split("/")
            self.expected_subnet = l[0]
            if len(l) == 2:
                self.expected_subnet_mask = l[1]
            else:
                self.expected_subnet_mask = ""
        else:
            self.expected_subnet = ""
            self.expected_subnet_mask = ""

        self.wifi = dict(mac_addr = '', ip_addr = '')

    def _cfgGetTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.conf['check_status_timeout']
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        #logging.info("Remove all Wlan Groups on the Zone Director.")
        #lib.zd.wgs.remove_wlan_groups(self.zd, self.testbed.get_aps_sym_dict_as_mac_addr_list())
        #logging.info("Remove all WLAN on the Zone Director.")
        self.zd.remove_all_cfg()

    def _cfgGetActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = None
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in testbed." % self.conf['active_ap'])
            self.active_ap_mac = self.active_ap.base_mac_addr.lower()
            if self.connection_mode:
                self.testbed.verify_ap_connection_mode(self.active_ap.base_mac_addr.lower())

    def _cfgCreateAuthenticationMethod(self):
        if self.wlan_cfg['ras_addr']:
            logging.info("Create a radius authentication server on the ZD")
            self.zd.create_radius_server(self.wlan_cfg['ras_addr'], self.wlan_cfg['ras_port'], self.wlan_cfg['ras_secret'])
        elif self.wlan_cfg['ad_addr']:
            logging.info("Create an AD server on the ZD")
            self.zd.create_ad_server(self.wlan_cfg['ad_addr'], self.wlan_cfg['ad_port'], self.wlan_cfg['ad_domain'])
        else:
            logging.info("Create a user on the ZD")
            self.zd.create_user(
                self.wlan_cfg['username'], self.wlan_cfg['password'])

    def _cfg_wlanForAP(self):
        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        if self.wlan_cfg['do_tunnel']:
            logging.info("The WLAN has tunnel enabled")
        if self.wlan_cfg.has_key('vlan_id'):
            logging.info("The WLAN has VLAN tagging enabled with VID %s" % self.wlan_cfg['vlan_id'])
        self.zd.cfg_wlan(self.wlan_cfg)
        #tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')
        # make sure wlan_cfg['ssid'] is not belong to default wlanGroups
        # so we can isolate an AP to wlan_cfg['ssid'] -- to make 1Wlan 1AP possible
        lib.zd.wgs.uncheck_default_wlan_member(self.zd,
                                           self.wlan_cfg['ssid'])

    def _testWlanIsUp(self):
        self.errmsg = tmethod8.check_wlan_on_ap_is_up(self.active_ap,
                                                  self.wlan_cfg['ssid'],
                                                  self.conf['check_wlan_timeout'])

    def _isolateAPWithWlanGroups(self):
        (self.wgs_info, self.wgs_apinfo, self.ap_xstatus) = \
            tmethod8.assign_1ap_to_1wlan_with_wlan_groups(self.zd,
                                                         self.active_ap_mac,
                                                         self.wlan_cfg,
                                                         self.wgs_cfg)
        tmethod8.pause_test_for(10, 'Wait for ZD to push config to the APs')


    # client is connected if not self.errmsg
    def _configClientToAssocWlan(self):
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

# Test method design statment
#
#   Every test method return empty string to indicate an OK status, good to proceed to next step.
#   Test method return the error message to the caller which in turn may return ('FAIL', self.errmsg)
#   The error message should be set in the class instance variable name self.errmsg.
#   This method just to make the statment in the test() looks clean.
#
    def _testRemoveNonActiveAPWlanAndVerifyActiveAPHasWlanUp(self):
        self.errmsg = tmethod.verify_wlan_on_aps(self.active_ap, self.wlan_cfg['ssid'], self.testbed.components['AP'])

    def _testIfVlanCheckClientAndDestAtSameSubnet(self):
        # Check if the wireless IP address of the station belongs to the subnet of the parameter 'ip'.
        self.errmsg = ""
        if self.expected_subnet:
            sta_wifi_subnet = utils.get_network_address(self.wifi['ip_addr'], self.expected_subnet_mask)
            if sta_wifi_subnet != self.expected_subnet:
                self.errmsg = "The wireless IP address '%s' of the target station was not as expected '%s'" % \
                              (self.wifi['ip_addr'], self.expected_subnet)
        elif self.conf.has_key('vlan_id'):
            sta_wifi_subnet = utils.get_network_address(self.wifi['ip_addr'], self.expected_subnet_mask)
            expected_subnet = utils.get_network_address(self.dest_ip, self.expected_subnet_mask)
            if sta_wifi_subnet != expected_subnet:
                self.errmsg = "The wireless IP address '%s' of target station %s has different subnet with '%s'" % \
                              (self.wifi['ip_addr'], self.target_station.get_ip_addr(), self.dest_ip)

    def _testClientShouldNotReachDest(self):
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.test_ip_addr, ping_timeout_ms = 5000)

    def _testVerifyZDClientIsUnauthorized(self):
        # In Web authentication, when client is unauthorized, the ZD shows IP address of the client
        (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_unauthorized(self.zd,
                                                                       self.wifi['ip_addr'], self.wifi['mac_addr'],
                                                                       self.conf['check_status_timeout'])

    def _testClientAllowToReachDest(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.test_ip_addr, ping_timeout_ms = self.conf['ping_timeout'] * 1000)

    def _cfgStationPerformWebAuth(self):
        logging.info("Perform Web authentication on the target station %s" % self.target_station.get_ip_addr())
        arg = tconfig.get_web_auth_params(self.zd, self.wlan_cfg['username'], self.wlan_cfg['password'])
        self.target_station.perform_web_auth(arg)

    def _testVerifyZDClientIsAuthorized(self):
        # In Web authentication, after the client is authorized, the ZD shows username used to authenticate of the client
        (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_authorized(self.zd,
                                                                     self.wlan_cfg['username'], self.wifi['mac_addr'],
                                                                     self.conf['check_status_timeout'])

    def _testVerifyClientAssocProperly(self, client_info = None):
        if not client_info: client_info = self.client_info
        self.errmsg = ""
        if client_info['ip'] != self.wlan_cfg['username'] and client_info['ip'] != self.wlan_cfg['username']+"/"+self.wifi['ip_addr']:
            self.errmsg = "The station's username shown on ZD was %s instead of %s" % \
                    (client_info['ip'], self.wlan_cfg['username'])
            return

        if client_info['wlan'] != self.wlan_cfg['ssid']:
            self.errmsg = "The station's SSID shown on ZD is %s instead of %s" % \
                    (client_info['wlan'], self.wlan_cfg['ssid'])
            return

        if client_info['apmac'] == '00:00:00:00:00:00':
            self.errmsg = "MAC address of the active AP shown on ZD is incorrect (%s)" % client_info['apmac']
            return

    def _testClientIsAtActiveAP(self, client_info):
        self.errmsg = tmethod.verify_station_info_on_ap(self.active_ap, self.wifi['mac_addr'], self.wlan_cfg['ssid'],
                                            client_info['channel'])

    def _cfgCleanupSwitchMacTable(self):
        # This step ensures that the switch doesn't keep old entries which may be incorrect
        if self.testbed.components.has_key("L3Switch"):
            self.testbed.components["L3Switch"].clear_mac_table()

    def _testStationMacInTunnelMode(self):
        if self.active_ap:
            ap_mac = self.active_ap.base_mac_addr.lower()
        else:
            ap_mac = self.client_info_on_zd["apmac"].lower()
        sta_mac = self.wifi['mac_addr'].lower()

        try:
            self.errmsg = self.testbed.verify_station_mac_in_tunnel_mode(ap_mac, sta_mac, self.wlan_cfg["do_tunnel"])
        except Exception, e:
            self.errmsg = e.message

    def _cfgDeleteStationFromZD(self):
        logging.info("Delete wireless client from the ZD")
        if self.wifi['mac_addr']:
            self.zd.delete_clients(self.wifi['mac_addr'])

