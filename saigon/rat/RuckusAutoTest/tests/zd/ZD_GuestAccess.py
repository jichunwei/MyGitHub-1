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
import time

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class ZD_GuestAccess(Test):
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
        self._cfgInitTargetSation()

        # Clean up and record current configuration of the ZD
        self._cfgInitZoneDirector()

        # Clear the switch MAC table if the switch does exist in the test bed
        self._cfgCleanupSwitchMacTable()

    def test(self):
        # Configure guest policy and new WLAN on the ZD
        self._cfgSetupWlanZoneDirector()

        # Find the target AP if with given MAC/symbolic name/model/connection mode
        # Then remove all WLANs on other APs
        self._cfgActiveAP()

        # Configure the WLAN profile on the remote station
        self._cfgWlanOnStation()

        # Verify the IP address assigned to the wireless adapter on the target station
        self._testStaWifiIpAddress()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Verify the ability to send traffic before doing guest authentication
        self._testStationPingBeforeAuthen()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Verify information of the target station shown on the Zone Director before performing Guest Auth
        self._testVerifyStationInfoOnZDBeforeAuthen()
        if self.errmsg: return ("FAIL", self.errmsg)

        logging.info("Perform Guest authentication on the target station %s using guest pass '%s'" % \
                     (self.target_station.get_ip_addr(), self.guest_pass))
        
        self._start_browser_before_auth()
        if self.errmsg:
            return ("FAIL", self.errmsg)
        
        arg = tconfig.get_guest_auth_params(self.zd, self.guest_pass, self.use_tou, self.redirect_url)
#        self.target_station.perform_guest_auth(arg)
        if self.conf.get('target_url'):
            arg['target_url'] = self.conf['target_url']

        if self.conf.get('expected_data'):
            arg['expected_data'] = self.conf['expected_data']

        arg['no_auth'] = bool(self.conf.get('no_auth'))
        messages = self.target_station.perform_guest_auth_using_browser(self.browser_id, arg)
        messages = eval(messages)
        
        errmsg = ''
        passmsg = ''
        for m in messages.iterkeys():
            if messages[m]['status'] == False:
                errmsg += messages[m]['message'] + " "

            else:
                passmsg += messages[m]['message'] + " "

        if errmsg:
            return ("FAIL", errmsg)
        logging.info(passmsg)
        
        time.sleep(5)
        self._close_browser_after_auth()
        if self.errmsg:
            return ("FAIL", self.errmsg)
        
        # Verify the ability to send traffic before doing guest authentication
        self._testStationPingAfterAuthen()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Verify information of the target station shown on the Zone Director after performing Guest Auth
        self._testVerifyStationInfoOnZDAfterAuthen()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Verify the wireless client's MAC address to see if it is on ZD side or AP side
        self._testStationMacInTunnelMode()
        if self.errmsg: return ("FAIL", self.errmsg)

        return ("PASS", "")

    def cleanup(self):
        logging.info("Remove all the WLANs on the Zone Director")
        #self.zd.remove_all_cfg()

        #logging.info("Remove all Guest Passes created on the Zone Director")
        #self.zd.remove_all_guestpasses()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
#        if self.current_guest_access_policy:
#            logging.info("Restore Guest Access Policy to original configuration on ZD")
#            self.zd.set_guestaccess_policy(**self.current_guest_access_policy)
        logging.info('Remove all guest access profiles')
        self.zd.delete_guestaccess_policy()

        if self.current_guest_pass_policy:
            logging.info("Restore Guest Password Policy to original configuration on ZD")
            self.zd.set_guestpass_policy(**self.current_guest_pass_policy)

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
        # Define test parameters
        self.conf = {'target_url': "http://www.example.net/",
                     #@zj 20140721 fix  ZF-9286
                     #"http://172.16.10.252/",
                     'no_auth': False,
                     'expected_data': "It works!",
                     'browser_name': "firefox",
                     'start_browser_tries': 3,
                     'start_browser_timeout': 15,
                     }
        self.conf.update(conf)
        if conf.has_key('wlan_cfg'):
            self.wlan_cfg = conf['wlan_cfg']
            self.wlan_cfg['use_guest_access'] = True
        else:
            # Default security setting used for the test is open-none
            self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                             'sta_encryption': 'none', 'ras_addr': '', 'password': '', 'use_guest_access': True,
                             'ad_domain': '', 'ad_port': '', 'ssid': 'RAT-GUESTACCESS-TEST', 'key_string': '',
                             'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'wpa_ver': '', 'ras_secret': ''}
        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.test_ip = conf['ip']
        self.use_guest_auth = conf['use_guest_auth']
        self.use_tou = conf['use_tou']
        self.active_ap = None
        self.target_station = None
        self.zd = self.testbed.components['ZoneDirector']

        if conf.has_key('redirect_url'):
            self.redirect_url = conf['redirect_url']
        else:
            self.redirect_url = ''

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

    def _cfgInitZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)
        #logging.info("Remove all Guest Passes created on the Zone Director")
        #self.zd.remove_all_guestpasses()
        
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement
#        logging.info("Record current Guest Access Policy on the ZD")
#        self.current_guest_access_policy = self.zd.get_guestaccess_policy()
        logging.info('Remove all guest access profiles')
        self.zd.delete_guestaccess_policy()

        logging.info("Record current Guest Password Policy on the ZD")
        self.current_guest_pass_policy = self.zd.get_guestpass_policy()

    def _cfgInitTargetSation(self):
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(self.conf['target_station'],
                                               self.testbed.components['Station'],
                                               check_status_timeout = self.check_status_timeout,
                                               remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgSetupWlanZoneDirector(self):
        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        #@author: Jane.Guo @since: 2013-09 adapt to 9.8 guest access improvement

        logging.info("Configure Guest Access policy on the Zone Director")
        self.zd.create_guestaccess_policy(use_guestpass_auth = self.use_guest_auth,
                                     use_tou = self.use_tou,
                                     redirect_url = self.redirect_url)
        #remove default restrict lists
        lib.zdcli.guest_access.delete_a_guest_restrict_access(self.zdcli, 4)
        lib.zdcli.guest_access.delete_a_guest_restrict_access(self.zdcli, 3)
        lib.zdcli.guest_access.delete_a_guest_restrict_access(self.zdcli, 2)
        #@author: Jane.Guo @since: 2013-11 default subnet is valid, so need add one to allow zd subnet
        guest_conf = {'destination_address': '192.168.0.0/16', 'type': 'Allow', 'order': '1'}
        lib.zdcli.guest_access.config_guest_restrict_access(self.zdcli, '2',**guest_conf)

        if self.use_guest_auth:
            if self.auth_type == "local":
                logging.info("Create a user account on the Zone Director")
                logging.debug("Username: '%s' - Password: '%s'" % (self.username, self.password))
                self.zd.create_user(self.username, self.password)
                auth_serv = "Local Database"
            elif self.auth_type == "radius":
                logging.info("Create a Radius server on the Zone Director")
                auth_serv = self.auth_srv_addr
                self.zd.create_radius_server(self.auth_srv_addr, self.auth_srv_port, self.auth_srv_info, auth_serv)
            elif self.auth_type == "ad":
                logging.info("Create an Active Directory server on the Zone Director")
                auth_serv = self.auth_srv_addr
                self.zd.create_ad_server(self.auth_srv_addr, self.auth_srv_port, self.auth_srv_info, auth_serv)
            elif self.auth_type == "ldap":
                logging.info("Create an LDAP server on Zone Director")
                auth_serv = "LDAP Server"
                ldap_server_cfg = {'server_addr': self.auth_srv_addr,
                                   'server_port': self.auth_srv_port,
                                   'server_name': auth_serv,
                                   'ldap_search_base': self.auth_srv_info,
                                   'ldap_admin_dn': self.conf['ldap_admin_dn'],
                                   'ldap_admin_pwd': self.conf['ldap_admin_pwd'],
                                   }
                lib.zd.aaa.create_server(self.zd, **ldap_server_cfg)

            logging.info("Configure Guest Password policy on the Zone Director")
            self.zd.set_guestpass_policy(auth_serv = auth_serv)

            if self.wlan_cfg['do_tunnel']:
                logging.info("The WLAN has tunnel enabled")
            if self.wlan_cfg.has_key('vlan_id'):
                logging.info("The WLAN has VLAN tagging enabled with VID %s" % self.wlan_cfg['vlan_id'])
            self.zd.cfg_wlan(self.wlan_cfg)
        
            logging.info("Generate a Guest Pass on the ZD")
            if self.conf.has_key('use_static_key') and self.conf['use_static_key']:
                key = utils.make_random_string(16, type = "alnum")
            else:
                key = ""
            try:
                guest_pass_info = self.zd.generate_guestpass(self.username, self.password,
                                                            self.guest_name, "5", "Days", key = key)
            except Exception, e:
                msg = "Unable to to generate Guest Pass. The authentication server didn't exist. Or %s" % e.message
                raise Exception(msg)

            if key and guest_pass_info[0] != key:
                raise Exception("The static key was not generated properly")

            self.guest_pass = guest_pass_info[0]
        else:
            self.guest_pass = ""

    def _cfgActiveAP(self):
        # Get the Actice AP and disable all wlan interface (non mesh interface) in non active aps
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if self.active_ap:
                self.errmsg = tmethod.verify_wlan_on_aps(self.active_ap, self.wlan_cfg['ssid'], self.testbed.components['AP'])
            else:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])

            if self.connection_mode:
                logging.info("Verify the connection mode of the active AP %s" % self.active_ap.get_base_mac())
                self.testbed.verify_ap_connection_mode(self.active_ap.get_base_mac().lower())

    def _cfgWlanOnStation(self):
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_cfg, self.check_status_timeout)

    def _testStaWifiIpAddress(self):
        # Renew the IP address of the wireless adapter on the wireless station
        res, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)

        if not res:
            raise Exception(val2)

        self.sta_wifi_ip_addr = val1
        self.sta_wifi_mac_addr = val2.lower()

        self.errmsg = ""
        if self.expected_subnet:
            logging.info("Verify the subnet address of the wireless client")
            sta_wifi_ip_network_addr = utils.get_network_address(self.sta_wifi_ip_addr, self.expected_subnet_mask)
            if self.expected_subnet != sta_wifi_ip_network_addr:
                self.errmsg = "The leased IP address was '%s', which is not in the expected subnet '%s'" % \
                              (sta_wifi_ip_network_addr, self.expected_subnet)

    def _testStationPingBeforeAuthen(self):
        # In guest access authentication, when client is unauthorized, the ZD shows IP address of the client
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.test_ip, ping_timeout_ms = 5000)

    def _testVerifyStationInfoOnZDBeforeAuthen(self):
        (self.errmsg, self.client_info_on_zd) = tmethod.verify_zd_client_is_unauthorized(self.zd,
                                                                             self.sta_wifi_ip_addr, self.sta_wifi_mac_addr,
                                                                             self.check_status_timeout)

    def _testStationPingAfterAuthen(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.test_ip, ping_timeout_ms = self.ping_timeout * 1000)

    def _testVerifyStationInfoOnZDAfterAuthen(self):
        # In guest access authentication, after the client is authorized, the ZD shows username used to authenticate of the client
        (self.errmsg, self.client_info) = tmethod.verify_zd_client_is_authorized(self.zd,
                                                                     self.guest_name, self.sta_wifi_mac_addr,
                                                                     self.check_status_timeout)

    def _cfgCleanupSwitchMacTable(self):
        # This step ensures that the switch doesn't keep old entries which may be incorrect
        if self.testbed.components.has_key("L3Switch"):
            self.testbed.components["L3Switch"].clear_mac_table()

    def _testStationMacInTunnelMode(self):
        if self.active_ap:
            ap_mac = self.active_ap.get_base_mac().lower()
        else:
            ap_mac = self.client_info_on_zd["apmac"].lower()
        sta_mac = self.sta_wifi_mac_addr.lower()

        try:
            self.errmsg = self.testbed.verify_station_mac_in_tunnel_mode(ap_mac, sta_mac, self.wlan_cfg["do_tunnel"])
        except Exception, e:
            self.errmsg = e.message

    def _start_browser_before_auth(self):
        '''
        Start browser in station.
        '''
        try:
            logging.info("Try to start a %s browser on station" % (self.conf['browser_name']))
            self.browser_id = self.target_station.init_and_start_browser(self.conf['browser_name'],
                                                                         self.conf['start_browser_tries'], 
                                                                         self.conf['start_browser_timeout'])
        except Exception, ex:
            self.errmsg = ex.message
            
    def _close_browser_after_auth(self):
        try:
            logging.info("Try to close the browser on station")
            self.target_station.close_browser(self.browser_id)
            
        except Exception, ex:
            self.errmsg = ex.message
            
