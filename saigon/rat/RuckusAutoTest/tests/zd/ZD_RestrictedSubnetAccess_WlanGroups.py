# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_RestrictedSubnetAccess Test class tests the ability of a station to associate with an AP under ZD's control
with open security configuration and Guest Pass authentication mechanism. The ability to associate is confirmed
via a ping test.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'restricted_ip_list': 'List of IP addresses that are restricted from guest clients',
                    'zd_ip': 'IP address of Zone Director',
                    'allowed_ip': 'An IP address that is not restricted',
                    'target_station': 'IP address of target station',

   Result type: PASS/FAIL/ERROR
   Results: PASS: target station can associate, do Guest authentication, can ping to a destination that is not
                  in the restricted list, and can't ping to any destinations that are in the restricted list
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
       - Remove all guest passes if existed
   2. Test:
       - Configure a WLAN on the ZD with open security setting
       - Configure Guest Access policy and configure a user which will be used to generate guest pass
       - Go to page Restricted Subnet Access and enter the subnets that are specified to the list
       - Open another browser, browse to the Guest Pass Generation page and generate a guest pass
       - Configure the target station with given security setting
       - Wait until it gets associated and get IP and MAC addresses of the wireless adapter
       - Do Guest authentication with the generated guest pass from the station
       - Ping to the IP that is not in the restricted list, the ping should be done ok
       - Ping to the addresses that are in the restricted list and make sure that they can not be done
       - Ping to the ZD and this should not be done successfully either
   3. Cleanup:
       - Remove all wlan configuration and generated guest passes on ZD
       - Remove wireless profile on remote wireless STA
       - Verify that wireless station is completely disconnected after removing the wireless profile.

   How it is tested?
       - After the client has done the authentication successfully, go to the table Active Clients and delete that
         user. The script should report that the client cannot ping to the address that should be pingable
"""

import os
import re
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import Ratutils as utils

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_RestrictedSubnetAccess_WlanGroups(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'restricted_ip_list': 'List of IP addresses that are restricted from guest clients',
                           'zd_ip': 'IP address of Zone Director',
                           'allowed_ip': 'An IP address that are not restricted',
                           'target_station': 'IP address of target station'}

    def config(self, conf):
        self._cfgInitTestParams(conf)

        # Detect and prepare the target station
        self._cfgInitTargetStation()

        # Clean up and record current configuration of the ZD
        self._cfgInitZoneDirector()
        self._cfgActiveAP()

    def test(self):
        self._cfg_wlanForAP()
        self._isolateAPWithWlanGroups()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testWlanIsUp()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._cfgGuestAccessAndAuthenticationMethod()
        self._configClientToAssocWlan()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._get_clientWifiAddress()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testClientShouldNotReachDest()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyZDClientIsUnauthorized()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._cfgStationPerformGuestAuth()

        self._testClientAllowToReachDest()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testClientShouldNotReachZD()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testClientShouldNotReachRestritedList()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyZDClientIsAuthorized()
        if self.errmsg: return ('FAIL', self.errmsg)

        # Verify information of the target station shown on the AP if the parameter 'active_ap' is passed.
        self._testClientIsAtActiveAP(self.client_info)
        if self.errmsg: return ("FAIL", self.errmsg)
        msg = "ActiveAP[%s %s %s %s] can support Restricted Subnet Access with use_guest_auth[%s] use_tou[%s] redirect_url[%s]" \
            % (self.conf['active_ap'], self.active_ap.get_ap_model(),
                self.active_ap.get_base_mac(), self.active_ap.ip_addr,
                self.use_guest_auth, self.use_tou, self.redirect_url)
        return ('PASS', msg)

    def cleanup(self):
        self._cfgRemoveZDWlanGroupsAndWlan()
        self._restoreZDConfigure()


    def _cfgInitTestParams(self, conf):
        # Define test parameters
        self.conf = dict(ping_timeout = 10,
                          check_status_timeout = 240,
                          check_wlan_timeout = 30,
                          break_time = 3)
        self.conf.update(conf)
        if not self.conf.has_key('wlan_cfg'):
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg()
        if not self.conf.has_key('wgs_cfg'):
            self.conf['wgs_cfg'] = tmethod8.get_default_wlan_groups_cfg()
        self.errmsg = ''
        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid(self.conf['ssid'])
        self.wlan_cfg = self.conf['wlan_cfg']
        self.wlan_cfg['use_guest_access'] = True
        self.wgs_cfg = self.conf['wgs_cfg']
        self.test_ip_addr = conf['dest_ip']
        self.zd_ip = conf['zd_ip']
        self.restricted_ip_list = conf['restricted_ip_list']
        self.restricted_subnet_list = []
        self.zd = self.testbed.components['ZoneDirector']
        for ip in self.restricted_ip_list:
            self.restricted_subnet_list.append("%s/%s" % (utils.get_network_address(ip), utils.get_subnet_mask(ip)))
        self.redirect_url = ""
        self.use_guest_auth = self.conf['use_guest_auth']
        self.use_tou = self.conf['use_tou']
        self.username = "ruckus"
        self.password = "ruckus"
        self.guest_name = "Retriever"
        self.current_guest_access_policy = None
        self.current_guest_pass_policy = None
        self.current_restricted_list = None
        self.target_station = None
        if self.conf.has_key('connection_mode'):
            self.connection_mode = self.conf['connection_mode']
        else:
            self.connection_mode = ""

        if self.conf.has_key('enable_tunnel'):
            self.wlan_cfg['do_tunnel'] = self.conf['enable_tunnel']
        else:
            self.wlan_cfg['do_tunnel'] = False

        if self.conf.has_key('auth_type'):
            self.auth_type = self.conf['auth_type']
        else:
            self.auth_type = "local"

        if self.conf.has_key('auth_srv_addr'):
            self.auth_srv_addr = self.conf['auth_srv_addr']
        else:
            self.auth_srv_addr = ""

        if self.conf.has_key('auth_srv_port'):
            self.auth_srv_port = self.conf['auth_srv_port']
        else:
            self.auth_srv_port = ""

        if self.conf.has_key('auth_srv_info'):
            self.auth_srv_info = self.conf['auth_srv_info']
        else:
            self.auth_srv_info = ""

    def _cfgInitTargetStation(self):
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(self.conf['target_station'],
                                                       self.testbed.components['Station'],
                                                       check_status_timeout = self.conf['check_status_timeout'],
                                                       remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfg_wlanForAP(self):
        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        if self.wlan_cfg['do_tunnel']:
            logging.info("The WLAN has tunnel enabled")
        if self.wlan_cfg.has_key('vlan_id') and self.wlan_cfg['vlan_id']:
            logging.info("The WLAN has VLAN tagging enabled with VID %s" % self.wlan_cfg['vlan_id'])
        self.zd.cfg_wlan(self.wlan_cfg)
        lib.zd.wgs.uncheck_default_wlan_member(self.zd,
                                           self.wlan_cfg['ssid'])

    def _cfgActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = None
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in testbed." % self.conf['active_ap'])
            self.active_ap_mac = self.active_ap.get_base_mac().lower()

            if self.connection_mode:
                logging.info("Verify the connection mode of the active AP %s" % self.active_ap.get_base_mac())
                self.testbed.verify_ap_connection_mode(self.active_ap.get_base_mac().lower())

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

    def _testClientShouldNotReachDest(self):
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.test_ip_addr, ping_timeout_ms = 5000)

    def _testClientShouldNotReachZD(self):
        zd_ip_addr = self.testbed.components['ZoneDirector'].ip_addr
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, zd_ip_addr, ping_timeout_ms = 5000)

    def _testClientShouldNotReachRestritedList(self):
        logging.info("Ping to destinations in the restricted list from the target station %s" %
                     self.target_station.get_ip_addr())
        for ip in self.restricted_ip_list:
            logging.info("Ping to %s" % ip)
            ping_result = self.target_station.ping(ip, 5 * 1000)
            if ping_result.find("Timeout") != -1:
                logging.info("Ping FAILED. Correct behavior")
            else:
                logging.info("Ping OK. Incorrect behavior")
                self.errmsg = "The target station could ping to %s while it was in the restricted subnet" % ip

    def _testVerifyZDClientIsUnauthorized(self):
        # In Web authentication, when client is unauthorized, the ZD shows IP address of the client
        (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_unauthorized(self.zd,
                                                                       self.wifi['ip_addr'], self.wifi['mac_addr'],
                                                                       self.conf['check_status_timeout'])
    def _cfgStationPerformGuestAuth(self):
        logging.info("Perform Guest authentication on the target station %s using guest pass '%s'" % \
                     (self.target_station.get_ip_addr(), self.guest_pass))

        arg = tconfig.get_guest_auth_params(self.zd, self.guest_pass, self.use_tou, self.redirect_url)
        self.target_station.perform_guest_auth(arg)

    def _testClientAllowToReachDest(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.test_ip_addr, ping_timeout_ms = self.conf['ping_timeout'] * 1000)

    def _testStationPingAfterAuthen(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.test_ip, ping_timeout_ms = self.ping_timeout * 1000)

    def _testVerifyZDClientIsAuthorized(self):
        # In guest access authentication, after the client is authorized, the ZD shows username used to authenticate of the client
        (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_authorized(self.zd,
                                                                     self.guest_name, self.wifi['mac_addr'],
                                                                     self.conf['check_status_timeout'])

    def _testClientIsAtActiveAP(self, client_info):
        self.errmsg = tmethod.verify_station_info_on_ap(self.active_ap, self.wifi['mac_addr'], self.wlan_cfg['ssid'],
                                            client_info['channel'])

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        #logging.info("Remove all Wlan Groups on the Zone Director.")
        #lib.zd.wgs.remove_wlan_groups(self.zd, self.testbed.get_aps_sym_dict_as_mac_addr_list())
        #logging.info("Remove all WLAN on the Zone Director.")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

    def _cfgInitZoneDirector(self):
        self._cfgRemoveZDWlanGroupsAndWlan()

        logging.info("Record current configured restricted subnets on ZD")
        self.current_restricted_list = self.zd.get_restricted_subnets()

        logging.info("Record current Guest Access Policy on ZD")
        self.current_guest_access_policy = self.zd.get_guestaccess_policy()

        logging.info("Record current Guest Password Policy on the ZD")
        self.current_guest_pass_policy = self.zd.get_guestpass_policy()

        logging.info("Remove all Guest Pass created on the Zone Director")
        self.zd.remove_all_guestpasses()

    def _cfgGuestAccessAndAuthenticationMethod(self):
        logging.info("Configure Guest Access policy on the Zone Director")
        self.zd.set_guestaccess_policy(use_guestpass_auth = self.use_guest_auth,
                                                                     use_tou = self.use_tou,
                                                                     redirect_url = self.redirect_url)
        logging.debug("New Guest Access Policy use_guestpass_auth=%s --- use_tou=%s --- redirect_url=%s" %
                      (self.use_guest_auth, self.use_tou, self.redirect_url))

        logging.info("Configure Restricted Subnet Access on the Zone Director")
        self.zd.set_restricted_subnets(self.restricted_subnet_list)

        logging.info("Create a user on the Zone Director")
        self.zd.create_user(self.username, self.password)

        logging.info("Generate a Guest Pass on the ZD")
        self.guest_pass, self.expired_time = self.zd.generate_guestpass(self.username,
                                                             self.password,
                                                             self.guest_name, "1", "Days")

    def _restoreZDConfigure(self):
        if self.current_guest_access_policy:
            logging.info("Restore Guest Access Policy to original configuration on ZD")
            self.zd.set_guestaccess_policy(**self.current_guest_access_policy)

        if self.current_guest_pass_policy:
            logging.info("Restore Guest Password Policy to original configuration on ZD")
            self.zd.set_guestpass_policy(**self.current_guest_pass_policy)

        if self.current_restricted_list:
            logging.info("Restore original configured restricted subnets on ZD")
            self.zd.set_restricted_subnets(self.current_restricted_list)
