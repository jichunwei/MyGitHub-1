# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_GuestAccess Test class tests the ability of a station to associate with an AP under ZD's control
with open security configuration and Guest Pass authentication mechanism. The ability to associate is confirmed
via a ping test.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'ip': 'IP address to ping',
                    'target_station': 'ip address of target station',
                    'active_ap': 'symbolic name or mac address of active AP',
                    'use_guest_auth': 'Use Guest Pass access authentication or not',
                    'use_tou': 'Use Terms Of Use or not',
                    'redirect_url': 'Use this redirect URL',
                    'connection_mode': 'l2/l3, optional',
                    'enable_tunnel': 'True/False, optional',
                    'ap_model': 'AP model, optional',
                    'auth_type': 'local/radius/ad, optional',
                    'auth_srv_addr': 'authentication server address, optional',
                    'auth_srv_port': 'authentication server port, optional',
                    'auth_srv_info': 'extra information about authentication server, optional',
                    'auth_username': 'authentication username, optional',
                    'auth_password': 'authentication password, optional',
                    'expected_subnet': 'used to validate the leased IP address of wireless client, optional',
                    'vlan_id': 'VLAN ID assigned to the WLAN, optional'

   Result type: PASS/FAIL/ERROR
   Results: PASS: target station can associate, pass WebAuth, ping to a destination successfully and
                  information is shown correctly in ZD and AP
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
       - Remove all guest passes if existed
   2. Test:
       - Configure a WLAN on the ZD with open security setting
       - Configure Guest Access policy and configure a user which will be used to generate guest pass
       - Open another browser, browse to the Guest Pass Generation page and generate a guest pass
       - Configure the target station with given security setting
       - Wait until it gets associated and get IP and MAC addresses of the wireless adapter
       - Do a ping to make sure the AP doesn't forward the traffic from the station
       - Verify if the ZD shows correct information about the connected station
       - Do Guest authentication from the station
       - Do a ping again to make sure traffic gets forwarded
       - Verify if the ZD shows correct information about the connected station one more time
   3. Cleanup:
       - Remove all wlan configuration and generated guest passes on ZD
       - Remove wireless profile on remote wireless STA
       - Verify if wireless station is completely disconnected after removing the wireless profile

   How it is tested?
       - While the test is running, right after the guest pass is generated, go to the table Generated Guest Pass
         and remove it. The script should report that it is unable to do the Guest authentication on the remote
         station because the pass has been expired or invalid
       - After the client has done the authentication successfully, go to the table Active Clients and delete that
         user. The script should report that the ZD has incorrect info about the client
"""

import os
import re
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import Ratutils as utils

import lib_clean_up as rmhlp

class ZD_GuestAccess_WlanGroups(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'ip': 'IP address to ping',
                           'target_station': 'ip address of target station',
                           'active_ap': 'symbolic name or MAC address of active AP',
                           'use_guest_auth': 'Use Guest Pass access authentication or not',
                           'use_tou': 'Use Terms Of Use or not',
                           'redirect_url': 'Use this redirect URL',
                           'connection_mode': 'l2/l3, optional',
                           'enable_tunnel': 'True/False, optional',
                           'auth_type': 'local/radius/ad, optional',
                           'auth_srv_addr': 'authentication server address, optional',
                           'auth_srv_port': 'authentication server port, optional',
                           'auth_srv_info': 'extra information about authentication server, optional',
                           'auth_username': 'authentication username, optional',
                           'auth_password': 'authentication password, optional',
                           'expected_subnet': 'used to validate the leased IP address of wireless client, optional',
                           'vlan_id': 'VLAN ID assigned to the WLAN, optional'}

    def config(self, conf):
        # Prepare test parameters
        self._cfgInitTestParams(conf)

        # Detect and prepare the target station
        self._cfgInitTargetStation()

        # Clean up and record current configuration of the ZD
        self._cfgInitZoneDirector()
        self._cfgActiveAP()
        # Clear the switch MAC table if the switch does exist in the test bed
        self._cfgCleanupSwitchMacTable()

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

        self._testIfVlanCheckClientAndDestAtSameSubnet()
        if self.errmsg: return ("FAIL", self.errmsg)

        #@author: Jane.Guo @since: 2013-08 add default restricted subnet for zd
        restricted_subnet_list = ['192.168.0.0/16']
        self._set_guest_restricted_subnet(restricted_subnet_list)
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testClientShouldNotReachDest()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testVerifyZDClientIsUnauthorized()
        if self.errmsg: return ('FAIL', self.errmsg)
        
        #self._cfgStationPerformGuestAuth()
        logging.info("Perform Guest Pass authentication on the target station %s" % \
                     self.target_station.get_ip_addr())
        
        arg = tconfig.get_guest_auth_params(
                self.zd, self.guest_pass, self.use_tou, self.redirect_url
            )
        browser_id = int(self.target_station.init_and_start_browser())
        self.target_station.perform_guest_auth_using_browser(browser_id, arg)
        self.target_station.close_browser(browser_id)

        #always check Client is Authorized, but ignore its outcome
        self._testVerifyZDClientIsAuthorized()

        self._testClientAllowToReachDest()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testClientShouldNotReachZD()
        if self.errmsg: return ('FAIL', self.errmsg)

        # OK; if it is pingable; but client is not authorized; problem
        self._testVerifyZDClientIsAuthorized()
        if self.errmsg: return ('FAIL', self.errmsg)

        # Verify information of the target station shown on the AP if the parameter 'active_ap' is passed.
        self._testClientIsAtActiveAP(self.client_info)
        if self.errmsg: return ("FAIL", self.errmsg)

        # Verify the wireless client's MAC address to see if it is on ZD side or AP side
        self._testStationMacInTunnelMode()
        if self.errmsg: return ("FAIL", self.errmsg)

        msg = "ActiveAP[%s %s %s %s] can support GuestAuth with use_guest_auth[%s] use_tou[%s] redirect_url[%s]" \
            % (self.conf['active_ap'], self.active_ap.get_ap_model(),
                self.active_ap.base_mac_addr, self.active_ap.ip_addr,
                self.use_guest_auth, self.use_tou, self.redirect_url)
        return ('PASS', msg)

    def cleanup(self):
        self._cfgRemoveZDWlanGroupsAndWlan()
        self._restoreZDConfigure()

    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout = 10,
                          check_status_timeout = 240,
                          check_wlan_timeout = 30,
                          break_time = 3)
        self.conf.update(conf)
        if not self.conf.has_key('wlan_cfg'):
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg()
        if not self.conf.has_key('wgs_cfg'):
            self.conf['wgs_cfg'] = tmethod8.get_default_wlan_groups_cfg()
        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid(self.conf['ssid'])
        self.wlan_cfg = self.conf['wlan_cfg']
        self.wlan_cfg['use_guest_access'] = True
        self.wgs_cfg = self.conf['wgs_cfg']
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
        self.errmsg = ''
        self.test_ip_addr = conf['dest_ip']
        self.use_guest_auth = conf['use_guest_auth']
        self.use_tou = conf['use_tou']
        self.redirect_url = conf['redirect_url']

        if self.use_guest_auth:
            self.guest_name = "A Fancy Guest Name"

        else:
            self.guest_name = "guest"

        self.current_guest_access_policy = None
        self.current_guest_pass_policy = None

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

        self.username = "ruckus.test.user"
        self.password = "ruckus.test.user"
        if self.conf.has_key('auth_username'):
            self.username = self.conf['auth_username']
        if self.conf.has_key('auth_password'):
            self.password = self.conf['auth_password']

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

        if self.conf.has_key('vlan_id'):
            self.wlan_cfg['vlan_id'] = self.conf['vlan_id']

    def _cfgRemoveZDWlanGroupsAndWlan(self):
        #logging.info("Remove all Wlan Groups on the Zone Director.")
        #lib.zd.wgs.remove_wlan_groups(self.zd, self.testbed.get_aps_sym_dict_as_mac_addr_list())
        #logging.info("Remove all WLAN on the Zone Director.")
        #self.zd.remove_all_cfg()
        rmhlp.remove_all_cfg(self.zd, self.zdcli)

    def _cfgInitZoneDirector(self):
        self._cfgRemoveZDWlanGroupsAndWlan()

        logging.info("Remove all Guest Passes created on the Zone Director")
        self.zd.remove_all_guestpasses()

        logging.info("Record current Guest Access Policy on the ZD")
        self.current_guest_access_policy = self.zd.get_guestaccess_policy()

        logging.info("Record current Guest Password Policy on the ZD")
        self.current_guest_pass_policy = self.zd.get_guestpass_policy()

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

    def _cfgGuestAccessAndAuthenticationMethod(self):
        logging.info("Configure Guest Access policy on the Zone Director")
        self.zd.set_guestaccess_policy(use_guestpass_auth = self.use_guest_auth,
                                                                     use_tou = self.use_tou,
                                                                     redirect_url = self.redirect_url)

        if self.use_guest_auth:
            if self.auth_type == "local":
                logging.info("Create a user account on the Zone Director")
                logging.debug("Username: '%s' - Password: '%s'" % (self.username, self.password))
                self.zd.create_user(self.username, self.password)
                auth_serv = "Local Database"
            elif self.auth_type == "radius":
                logging.info("Create a Radius server on the Zone Director")
                auth_serv = self.auth_srv_addr
                self.zd.create_radius_server(self.auth_srv_addr, self.auth_srv_port,
                                                                         self.auth_srv_info, auth_serv)
            elif self.auth_type == "ad":
                logging.info("Create an Active Directory server on the Zone Director")
                auth_serv = self.auth_srv_addr
                self.zd.create_ad_server(self.auth_srv_addr, self.auth_srv_port,
                                                                     self.auth_srv_info, auth_serv)

            logging.info("Configure Guest Password policy on the Zone Director")
            self.zd.set_guestpass_policy(auth_serv = auth_serv)

            logging.info("Generate a Guest Pass on the ZD")
            try:
                guest_pass_info = self.zd.generate_guestpass(self.username, self.password,
                                                            self.guest_name, "5", "Days")
            except Exception, e:
                msg = "Unable to to generate Guest Pass. The authentication server didn't exist. Or %s" % e.message
                raise Exception(msg)

            self.guest_pass = guest_pass_info[0]
        else:
            self.guest_pass = ""

    def _cfgActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = None
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in testbed." % self.conf['active_ap'])
            self.active_ap_mac = self.active_ap.base_mac_addr.lower()

            if self.connection_mode:
                logging.info("Verify the connection mode of the active AP %s" % self.active_ap.base_mac_addr)
                self.testbed.verify_ap_connection_mode(self.active_ap.base_mac_addr.lower())

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

    def _set_guest_restricted_subnet(self, restricted_subnet_list):
        #@author: Jane.Guo @since: 2013-08 add default restricted subnet for zd
        try:
            logging.info("Configure the guest restricted subnet access on ZD")
            self.zd.set_restricted_subnets(restricted_subnet_list)
        except Exception, ex:
            self.errmsg = '[Configure the guest restricted subnet list failed] %s' % ex.message

    def _testClientShouldNotReachDest(self):
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.test_ip_addr, ping_timeout_ms = 5000)

    def _testClientShouldNotReachZD(self):
        zd_ip_addr = self.testbed.components['ZoneDirector'].ip_addr
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, zd_ip_addr, ping_timeout_ms = 5000)

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

    def _testVerifyZDClientIsAuthorized(self):
        # In guest access authentication, after the client is authorized, the ZD shows username used to authenticate of the client
        (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_authorized(self.zd,
                                                                     self.guest_name, self.wifi['mac_addr'],
                                                                     self.conf['check_status_timeout'])

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
            ap_mac = self.client_info["apmac"].lower()
        sta_mac = self.wifi['mac_addr'].lower()

        try:
            self.errmsg = self.testbed.verify_station_mac_in_tunnel_mode(ap_mac, sta_mac, self.wlan_cfg["do_tunnel"])
        except Exception, e:
            self.errmsg = e.message

    def _restoreZDConfigure(self):
        if self.current_guest_access_policy:
            logging.info("Restore Guest Access Policy to original configuration on ZD")
            self.zd.set_guestaccess_policy(**self.current_guest_access_policy)

        if self.current_guest_pass_policy:
            logging.info("Restore Guest Password Policy to original configuration on ZD")
            self.zd.set_guestpass_policy(**self.current_guest_pass_policy)

