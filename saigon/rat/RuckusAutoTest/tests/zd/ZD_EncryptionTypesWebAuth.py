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
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_EncryptionTypesWebAuth(Test):
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
        # Testing parameters
        self._cfgInitTestParams(conf)

        # Find the target station object
        self._cfgGetTargetStation()

        self._cfgRemoveZDWlan()

        # Find the active AP object if the parameter 'active_ap' is passed.
        self._cfgGetActiveAP()

        # Clear the mac table on the switch if it does exist in the test bed
        self._cfgCleanupSwitchMacTable()
        
        # remove all config 
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        
        #self.zd.remove_all_cfg()

    def test(self):
        self._cfgCreateAuthenticationMethod()

        self._createSSIDOnZoneDirector()

        self._testRemoveNonActiveAPWlanAndVerifyActiveAPHasWlanUp()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testStationAssocWithSSID()

        self._testRenewWifiIpAddress()
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

        return ("PASS", "")

    def cleanup(self):
        logging.info("Remove all the WLANs on the Zone Director")
        self.zd.remove_all_cfg()

        if self.target_station:
            logging.info("Remove all WLAN profiles on the remote station")
            self.target_station.remove_all_wlan()

            logging.info("Make sure the target station disconnects from the wireless networks")
            start_time = time.time()
            while True:
                if self.target_station.get_current_status() == "disconnected":
                    break
                time.sleep(1)
                if time.time() - start_time > self.check_status_timeout:
                    raise Exception("The station did not disconnect from wireless network within %d seconds" %
                        self.check_status_timeout)

    def _cfgInitTestParams(self, conf):
        if conf.has_key('wlan_cfg'):
            self.wlan_cfg = conf['wlan_cfg']
        else:
            # Get the default wlan configuration if the parameter 'wlan_cfg' is not passed.
            self.wlan_cfg = {'username': 'local.user', 'sta_auth': 'open', 'ras_port': '',
                             'key_index': '', 'auth': 'open', 'sta_encryption': 'none',
                             'ras_addr': '', 'password': 'local.user', 'ad_domain': '',
                             'ad_port': '', 'ssid': 'vlan_web_auth', 'key_string': '',
                             'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '',
                             'wpa_ver': '', 'ras_secret': '', 'vlan_id': ''}

        self.zd = self.testbed.components['ZoneDirector']
        self.conf = conf
        self.wlan_cfg['use_web_auth'] = True
        self.ping_timeout_ms = int(conf['ping_timeout_ms']) if conf.has_key('ping_timeout_ms') else 60000
        self.check_status_timeout = int(conf['check_status_timeout']) if conf.has_key('check_status_timeout') else 360

        tmp_list = self.conf['ip'].split("/")
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
            
        self.ldap_admin_dn = self.conf['ldap_admin_dn'] if self.conf.has_key('ldap_admin_dn') else ""
        self.ldap_admin_pwd = self.conf['ldap_admin_pwd'] if self.conf.has_key('ldap_admin_pwd') else ""            

        if conf.has_key('auth_username'):
            self.username = conf['auth_username']
        else:
            self.username = self.wlan_cfg['username']

        if conf.has_key('auth_password'):
            self.password = conf['auth_password']
        else:
            self.password = self.wlan_cfg['password']

    def _cfgGetTargetStation(self):
        self.target_station = tconfig.get_target_station(
                                  self.conf['target_station'],
                                  self.testbed.components['Station'],
                                  check_status_timeout=self.check_status_timeout,
                                  remove_all_wlan=True)

        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgRemoveZDWlan(self):
        logging.info("Remove all WLAN on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

    def _cfgGetActiveAP(self):
        self.active_ap = None
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])
            if self.connection_mode:
                self.testbed.verify_ap_connection_mode(self.active_ap.base_mac_addr.lower())

    def _cfgCreateAuthenticationMethod(self):
        if self.wlan_cfg['ras_addr']:
            logging.info("Create a radius authentication server on the ZD")
            self.zd.create_radius_server(
                self.wlan_cfg['ras_addr'], self.wlan_cfg['ras_port'], self.wlan_cfg['ras_secret'])
        elif self.wlan_cfg['ad_addr']:
            logging.info("Create an AD server on the ZD")
            self.zd.create_ad_server(
                self.wlan_cfg['ad_addr'], self.wlan_cfg['ad_port'], self.wlan_cfg['ad_domain'])
        else:
            logging.info("Create a user on the ZD")
            self.zd.create_user(
                self.wlan_cfg['username'], self.wlan_cfg['password'])

        if self.auth_type == "ldap":
            logging.info("Create an LDAP server on Zone Director")
            auth_serv = self.auth_srv_addr
            ldap_server_cfg = {'server_addr': self.auth_srv_addr,
                               'server_port': self.auth_srv_port,
                               'server_name': auth_serv,
                               'ldap_search_base': self.auth_srv_info,
                               'ldap_admin_dn': self.ldap_admin_dn,
                               'ldap_admin_pwd': self.ldap_admin_pwd,}

            lib.zd.aaa.create_server(self.zd, **ldap_server_cfg)            


    def _createSSIDOnZoneDirector(self):
        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        self.zd.cfg_wlan(self.wlan_cfg)
        if self.auth_type == "ldap":
            lib.zd.wlan.edit_wlan(self.zd, self.wlan_cfg['ssid'], {'auth_svr':self.auth_srv_addr})
        #JLIN@20081219 add delay time from 3 sec to 10 sec, ZD8.0 need to more to deploy setting to AP
        time.sleep(10)

# Test method design statment
#
#   Every test method return empty string to indicate an OK status, good to proceed to next step.
#   Test method return the error message to the caller which in turn may return ('FAIL', self.errmsg)
#   The error message should be set in the class instance variable name self.errmsg.
#   This method just to make the statment in the test() looks clean.
#
    def _testRemoveNonActiveAPWlanAndVerifyActiveAPHasWlanUp(self):
        self.errmsg = tmethod.verify_wlan_on_aps(self.active_ap, self.wlan_cfg['ssid'], self.testbed.components['AP'])

    def _testStationAssocWithSSID(self):
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_cfg, self.check_status_timeout)

    def _testRenewWifiIpAddress(self):
        (self.anOK, self.sta_wifi_ip_addr, self.sta_wifi_mac_addr) = \
        (self.anOK, self.xtype, self.errmsg) = \
            tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)

        # we use self.errmsg to indicate method PASS or FAIL; so set to '' if everything is an OK
        if self.anOK:
            self.errmsg = ''
            return self.errmsg
        elif self.xtype == 'FAIL':
            return self.errmsg
        else:
            raise Exception(self.errmsg)

    def _testIfVlanCheckClientAndDestAtSameSubnet(self):
        # Check if the wireless IP address of the station belongs to the subnet of the parameter 'ip'.
        self.errmsg = ""
        if self.expected_subnet:
            sta_wifi_subnet = utils.get_network_address(self.sta_wifi_ip_addr, self.expected_subnet_mask)
            if sta_wifi_subnet != self.expected_subnet:
                self.errmsg = "The wireless IP address '%s' of the target station was not as expected '%s'" % \
                              (self.sta_wifi_ip_addr, self.expected_subnet)
        elif self.conf.has_key('vlan_id'):
            sta_wifi_subnet = utils.get_network_address(self.sta_wifi_ip_addr, self.expected_subnet_mask)
            expected_subnet = utils.get_network_address(self.test_ip_addr, self.expected_subnet_mask)
            if sta_wifi_subnet != expected_subnet:
                self.errmsg = "The wireless IP address '%s' of target station %s has different subnet with '%s'" % \
                              (self.sta_wifi_ip_addr, self.target_station.get_ip_addr(), self.test_ip_addr)

    def _testClientShouldNotReachDest(self):
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.test_ip_addr, ping_timeout_ms = 5000)

    def _testVerifyZDClientIsUnauthorized(self):
        # In Web authentication, when client is unauthorized, the ZD shows IP address of the client
        (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_unauthorized(
                                              self.zd,
                                              self.sta_wifi_ip_addr, self.sta_wifi_mac_addr,
                                              self.check_status_timeout)

    def _testClientAllowToReachDest(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station,
                                                          self.test_ip_addr,
                                                          ping_timeout_ms=self.ping_timeout_ms)

    def _cfgStationPerformWebAuth(self):
        logging.info("Perform Web authentication on the target station %s" % self.target_station.get_ip_addr())

        arg = tconfig.get_web_auth_params(self.zd, self.username, self.password)
        self.target_station.perform_web_auth(arg)


    def _testVerifyZDClientIsAuthorized(self):
        # In Web authentication, after the client is authorized, the ZD shows username used to authenticate of the client
        (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_authorized(
                                              self.zd,
                                              self.username, self.sta_wifi_mac_addr,
                                              self.check_status_timeout)

    def _testVerifyClientAssocProperly(self, client_info = None):
        if not client_info: client_info = self.client_info
        self.errmsg = ""
        if client_info['ip'] != self.username and client_info['ip'] != self.username+'/'+self.sta_wifi_ip_addr:
            self.errmsg = "The station's username shown on ZD was %s instead of %s" % \
                    (client_info['ip'], self.username)
            return

        if client_info['wlan'] != self.wlan_cfg['ssid']:
            self.errmsg = "The station's SSID shown on ZD is %s instead of %s" % \
                    (client_info['wlan'], self.wlan_cfg['ssid'])
            return

        if client_info['apmac'] == '00:00:00:00:00:00':
            self.errmsg = "MAC address of the active AP shown on ZD is incorrect (%s)" % client_info['apmac']
            return

    def _testClientIsAtActiveAP(self, client_info):
        if self.active_ap:
            self.errmsg = tmethod.verify_station_info_on_ap(
                              self.active_ap, self.sta_wifi_mac_addr,
                              self.wlan_cfg['ssid'], client_info['channel'])

    def _cfgCleanupSwitchMacTable(self):
        # This step ensures that the switch doesn't keep old entries which may be incorrect
        if self.testbed.components.has_key("L3Switch"):
            self.testbed.components["L3Switch"].clear_mac_table()

    def _testStationMacInTunnelMode(self):
        if self.active_ap:
            ap_mac = self.active_ap.base_mac_addr.lower()
        else:
            ap_mac = self.client_info["apmac"].lower()
        sta_mac = self.sta_wifi_mac_addr.lower()

        try:
            self.errmsg = self.testbed.verify_station_mac_in_tunnel_mode(ap_mac, sta_mac, self.wlan_cfg["do_tunnel"])
        except Exception, e:
            self.errmsg = e.message

