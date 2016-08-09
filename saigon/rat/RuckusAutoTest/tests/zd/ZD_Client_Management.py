# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description:
   ZD_Client_Management script is used to management the clients access to an
   Guest Access enabled WLAN.
   It supports delete or block or unblock clients.

Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
        'ip': IP address of the host that client will be ping to
        'active_ap': The active ap symbolic name or mac address
        'target_station': The IP address of target station
        'test_option': the expect function will be test [delete/block/unblock]
        'connection_mode': L2/L3 connection mode of the AP
        'enable_tunnel': Use tunnel mode or not (True/False)
        'vlan_id': The vlan id that be applied / None if don't test with vlan
        'expected_subnet': The expected subnet that client will connect
        'test_policy': Web Authentication / Guest Access policy

   Result type: PASS/FAIL/ERROR

   Results: PASS: if all verify step is successful
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria
             that is not satisfied

   Test procedure:
   1. Config:
       - Clean the test environtment on ZD and Client.
   2. Test:
       - Create an guest association for testing
       - Do the Delete/Block or Unblock test with the existing connection
   3. Cleanup:
       - Cleanup the test environtment on ZD system

   How it is tested?
       -
"""
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.components import Helpers as lib


class ZD_Client_Management(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
        'ip': 'IP address of the host that client will be ping to',
        'active_ap': 'The active ap symbolic name or mac address',
        'target_station': 'The IP address of target station',
        'test_option': 'the expect function will be test [delete/block/unblock]',
        'connection_mode': 'L2/L3 connection mode of the AP',
        'enable_tunnel': 'Use tunnel mode or not (True/False)',
        'vlan_id': 'The vlan id that be applied / None if don not test with vlan',
        'expected_subnet': 'The expected subnet that client will connect',
        'test_policy': 'Web Authentication / Guest Access policy',
    }

    def config(self, conf):
        self._initTestParams(conf)

        self._cfgTargetStation()

        self._cfgZoneDirector()


    def test(self):
        self._cfgWlan()

        self._getGuestPassandExpiredTime()

        # Turn off all wlan interface on non active APs.
        self._cfgActiveAPs()

        # Process an association for the testing
        self._verifyAssociation()
        if self.errmsg:
            return ('FAIL', self.errmsg)

        # Client management testing
        self.test_function[self.test_option]()
        if self.errmsg:
            return ('FAIL', self.errmsg)

        else:
            return ('PASS', '')

    def cleanup(self):
        # Remove on non default setting on Zone Director
        self._cleanupTheZoneDirectorSetting()

        if self.target_station:
            logging.info("Remove all WLAN profiles on the remote station")
            self.target_station.remove_all_wlan()


    def _initTestParams(self, conf):
        # Define test parameters
        # Security setting used for the test is open-none
        self.conf = dict(ping_timeout = 15,
                         check_status_timeout = 240,
                         sta_getstatus_interval = 6,)
        self.conf.update(conf)

        self.ping_timeout_ms = self.conf['ping_timeout'] * 1000
        self.check_status_timeout = self.conf['check_status_timeout']
        self.sta_getstatus_interval = self.conf['sta_getstatus_interval']

        self.zd = self.testbed.components['ZoneDirector']
        self.target_station = None
        self.errmsg = ''
        self.test_option = conf['test_option']

        self.ip_addr = conf['ip']
        self.username = 'odessa'
        self.password = 'odessa'

        if self.conf['test_policy'] == 'guest access':
            logging.info('Prepare test parameters for the test using '
                         'Guest Access policy')
            self._initGuestAccessParameters()

        elif self.conf['test_policy'] == 'web authentication':
            logging.info('Prepare test parameters for the test using '
                         'Web Authentication policy')
            self._initWebAuthParameters()

        elif self.conf['test_policy'] == 'mac authentication':
            logging.info('Prepare test parameters for the test using '
                         'MAC Authentication policy')
            self._initMACAuthetication()

        if self.conf.has_key('connection_mode'):
            self.connection_mode = self.conf['connection_mode']
        else:
            self.connection_mode = ''

        self.test_function = {'delete': self._testDeleteClient,
                              'block': self._testBlockClient,
                              'unblock': self._testUnblockClient}


    def _initGuestAccessParameters(self):
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '',
                         'key_index': '', 'auth': 'open',
                         'sta_encryption': 'none', 'ras_addr': '', 'password': '',
                         'ad_domain': '', 'ad_port': '', 'key_string': '',
                         'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '',
                         'wpa_ver': '', 'ras_secret': ''}

        self.wlan_cfg['use_guest_access'] = True
        self.wlan_cfg['ssid'] = 'Guest Access testing - %s' % time.strftime("%H%M%S")
        self.use_guest_auth = True
        self.use_tou = True
        self.active_ap = None
        self.redirect_url = ''
        self.guest_name = 'ChiHuaHua'
        self.current_guest_access_policy = None
        self.current_guest_pass_policy = None


    def _initWebAuthParameters(self):
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '',
                         'key_index': '', 'auth': 'open',
                         'sta_encryption': 'none', 'ras_addr': '', 'password': '',
                         'ad_domain': '', 'ad_port': '', 'key_string': '',
                         'sta_wpa_ver': '', 'encryption': 'none', 'ad_addr': '',
                         'wpa_ver': '', 'ras_secret': ''}

        self.wlan_cfg['use_web_auth'] = True
        self.wlan_cfg['ssid'] = 'Web Authen testing - %s' % time.strftime("%H%M%S")


    def _initMACAuthetication(self):
        self.wlan_cfg = {'auth': 'mac', 'encryption': 'none'}
        self.wlan_cfg['ssid'] = 'MAC Authen testing - %s' % time.strftime("%H%M%S")


    def _cfgTargetStation(self):
        # Find the target station object and remove all Wlan profiles on it
        self.target_station = tconfig.get_target_station(
                                  self.conf['target_station'],
                                  self.testbed.components['Station'],
                                  check_status_timeout = self.check_status_timeout,
                                  remove_all_wlan = True,)

        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])


    def _cfgActiveAPs(self):
        # Get the active APs and disable all wlan interface
        # (non mesh interface) in non active APs
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            active_ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['active_ap'])
            if self.active_ap:
                for ap in self.testbed.components['AP']:
                    if ap is not self.active_ap:
                        logging.info("Remove all WLAN on non-active AP %s" % ap.get_base_mac())
                        ap.remove_all_wlan()

                logging.info("Verify WLAN status on the active AP %s" % active_ap_mac)
                if not self.active_ap.verify_wlan():
                    raise Exception("WLAN %s on active AP %s is not up" % \
                                    (self.active_ap.ssid_to_wlan_if(self.wlan_cfg['ssid']),
                                     active_ap_mac))

            else:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])

            # Check and configure the connection mode status of the active AP.
            #JLIN@20090806 if ap mgmt vlan enable, skip check the connection_mode
            mgmt_vlan = lib.zd.mvlan.get_ap_mgmt_vlan_info(self.zd)['mgmt_vlan']
            if self.connection_mode and mgmt_vlan['disabled']:
                ap_info = lib.zd.aps.get_ap_detail_info_by_mac_addr(self.zd, active_ap_mac)
                self.active_ap_conn_mode = ap_info['tunnel_mode']

                if self.active_ap_conn_mode.lower() != self.connection_mode.lower():
                    self.testbed.configure_ap_connection_mode(active_ap_mac,
                                                              self.connection_mode)
                    self.testbed.verify_ap_connection_mode(active_ap_mac)

        else:
            msg = 'The "active_ap" variable does not exist, the test process can not complete'
            raise Exception(msg)

    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        if self.conf.get('test_policy') == 'guest access':
            logging.info("Remove all Guest Passes created on the Zone Director")
            self.zd.remove_all_guestpasses()

            logging.info("Record current Guest Access Policy on the ZD")
            self.current_guest_access_policy = self.zd.get_guestaccess_policy()

            logging.info("Record current Guest Pass Policy on the ZD")
            self.current_guest_pass_policy = self.zd.get_guestpass_policy()

        logging.info('Unblock all blocked clients')
        self.zd.unblock_clients('')

        if self.wlan_cfg.get('use_guest_access'):
            # Configure the Guest Access policy on the Zone Director
            logging.info('Testing with Guest Access policy')
            self._cfgGuestAccessPolicy()

        elif self.wlan_cfg.get('use_web_auth'):
            # Configure the Guest Access policy on the Zone Director
            logging.info('Testing with Web Authentication policy')
            self._cfgWebAuthPolicy()

        elif self.wlan_cfg.get('auth') == 'mac':
            # Configure the MAC Authentication server on the Zone Director
            logging.info('Testing with MAC Authentication')
            self._cfgMacAuth()


    def _cfgWlan(self):
        """
        """
        logging.info("Configure a WLAN with SSID %s on the Zone Director" % \
                     self.wlan_cfg['ssid'])
        if self.wlan_cfg.get('do_tunnel'):
            logging.info("The WLAN has tunnel enabled")

        if self.wlan_cfg.get('vlan_id'):
            logging.info("The WLAN has VLAN tagging enabled with VID %s" % \
                         self.wlan_cfg['vlan_id'])

        if self.wlan_cfg['auth'] == 'mac':
            logging.info('The WLAN is for MAC Authentication')
            lib.zd.wlan.create_wlan(self.zd, self.wlan_cfg)
            return

        if self.wlan_cfg.get('use_guest_access') == True:
            logging.info('The WLAN is for Guest Access')

        elif self.wlan_cfg.get('use_web_auth') == True:
            logging.info('The WLAN is for Web Authentication')

        self.zd.cfg_wlan(self.wlan_cfg)


    def _cfgMacAuth(self):
        """
        """
        auth_server = {'server_addr': '192.168.0.252',
                       'server_port': '1812',
                       'server_name': 'freeRadius',
                       'radius_auth_secret': '1234567890'}

        logging.info('Configure the external server on Zone Director')
        lib.zd.aaa.create_server(self.zd, **auth_server)


    def _cfgGuestAccessPolicy(self):
        """
        """
        logging.info("Configure Guest Access policy on the Zone Director")
        self.zd.set_guestaccess_policy(use_guestpass_auth = self.use_guest_auth,
                                       use_tou = self.use_tou,
                                       redirect_url = self.redirect_url)

        logging.debug("New Guest Access Policy \
                      use_guestpass_auth=%s --- \
                      use_tou=%s --- \
                      redirect_url=%s" %
                      (self.use_guest_auth, self.use_tou, self.redirect_url))

        if self.use_guest_auth:
            logging.info("Create a user on the Zone Director")
            self.zd.create_user(self.username, self.password)

            logging.info("Configure Guest Pass policy on the Zone Director")
            self.zd.set_guestpass_policy(auth_serv = "Local Database")

        else:
            self.guest_pass = ""


    def _getGuestPassandExpiredTime(self):
        """
        """
        gp_cfg = {'username': self.username,
                  'password': self.password,
                  'wlan': self.wlan_cfg['ssid'],
                  'duration': '1',
                  'duration_unit': 'Days',
                  }
        if self.conf['test_policy'] == 'guest access':
            logging.info("Generate a Guest Pass on the ZD")
            lib.zd.ga.generate_guestpass(self.zd, **gp_cfg)

            self.guest_pass = lib.zd.ga.guestpass_info['single_gp']['guest_pass']
            self.expired_time = lib.zd.ga.guestpass_info['single_gp']['expired_time']

        else:
            self.guest_pass = ""


    def _cfgWebAuthPolicy(self):
        """
        """
        logging.info("Configure Web Authentication policy on the Zone Director")
        logging.info("Create a user on the Zone Director")
        self.zd.create_user(self.username, self.password)


    def _testDeleteClient(self):
        """
        """
        # Clear all event before testing
        self.zd.clear_all_events()

        # Delete the client entry
        self.zd.delete_clients(self.sta_wifi_mac_addr)

        # Verify the client deleted client events
        all_events = self.zd.get_events()

        if self.conf['test_policy'] == 'guest access':
            user_name = self.guest_name

        elif self.conf['test_policy'] == 'web authentication':
            user_name = self.username

        elif self.conf['test_policy'] == 'mac authentication':
            user_name = self.sta_wifi_mac_addr

        #MSG_client_del_by_admin={user} disconnected by admin from {wlan} at {ap}
        event = self.zd.messages['MSG_client_del_by_admin']
        event = event.replace('{user}', 'User[%s]' % user_name)
        event = event.replace('{wlan}', 'WLAN[%s]' % self.wlan_cfg['ssid'])
        event = event.replace('{ap}', '')
        exp_activity = event.lower()
        for event in all_events:
            findevent = str(event).lower().find(exp_activity)
            if findevent > 0:
                logging.info('The event "%s" is recorded on the Events table' % \
                             event)
                self.errmsg = ''
                return

        self.errmsg = 'Client [%s] is not deleted successfully' % \
                      self.sta_wifi_mac_addr

    def _testBlockClient(self):
        """
        """
        self.zd.block_clients(self.sta_wifi_mac_addr)
        # verify if the block station could re associate to the wlan
        logging.info("Configure a WLAN with SSID %s on the target station %s" % \
                     (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))

        # remove wlan configuration on client
        self._cfgTargetStation()

        logging.info("Make sure the station can not associate to the WLAN")
        self.target_station.cfg_wlan(self.wlan_cfg)
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "connected":
                self.errmsg = 'The blocked client [%s] could associate to the wlan' % \
                              self.sta_wifi_mac_addr
                return

            time.sleep(self.sta_getstatus_interval)
            if time.time() - start_time > self.check_status_timeout:
                self.errmsg = ''
                return

    def _testUnblockClient(self):
        """
        """
        # Block the client for testing
        self.zd.block_clients(self.sta_wifi_mac_addr)

        # remove wlan configuration on client
        self._cfgTargetStation()

        # Refresh the connection
        self.target_station.cfg_wlan(self.wlan_cfg)
        time.sleep(3 * self.sta_getstatus_interval)
        if self.target_station.get_current_status() == "connected":
            self.errmsg = 'Client [%s] is blocked but the connection is existing' % \
                          self.sta_wifi_mac_addr
            return

        # Unblock the blocked client
        self.zd.unblock_clients(self.sta_wifi_mac_addr)

        # Verify the station could re-associate to the wlan
        self._verifyAssociation()

        self.errmsg = ''


    def _verifyAssociation(self):
        """
        """
        if self.wlan_cfg.get('use_guest_access') == True:
            self._verifyGuestAccess()

        elif self.wlan_cfg.get('use_web_auth') == True:
            self._verifyWebAuthentication()

        elif self.wlan_cfg.get('auth') == 'mac':
            self._verifyMACAuthentication()


    def _verifyMACAuthentication(self):
        self._verifyStationConnection()
        if self.errmsg:
            return

        logging.info("Try to ping to %s from the target station %s one more time" % \
                     (self.ip_addr, self.target_station.get_ip_addr()))

        self.errmsg = tmethod.client_ping_dest_is_allowed(
                          self.target_station,
                          self.ip_addr,
                          ping_timeout_ms = self.ping_timeout_ms)

        if self.errmsg:
            return

        # Verify information of the target station shown on the Zone Director one more time
        expected_status = 'Authorized'
        expected_user_info = self.sta_wifi_ip_addr
        expected_client_info = {'ip': expected_user_info, 'status': expected_status}

        self.errmsg, sta_info = tmethod.verify_zd_client_status(
                                    self.zd, self.sta_wifi_mac_addr,
                                    expected_client_info, self.check_status_timeout)


    def _verifyWebAuthentication(self):
        self._verifyStationConnection()
        if self.errmsg:
            return

        logging.info("Ping to %s from the target station" % self.ip_addr)
        self.errmsg = tmethod.client_ping_dest_not_allowed(
                          self.target_station,
                          self.ip_addr,
                          ping_timeout_ms = self.ping_timeout_ms)
        if self.errmsg:
            return

        # Verify information of the target station shown on the Zone Director
        expected_status = 'Unauthorized'
        expected_user_info = self.sta_wifi_ip_addr
        expected_client_info = {'ip': expected_user_info, 'status': expected_status}

        self.errmsg, sta_info = tmethod.verify_zd_client_status(
                                    self.zd, self.sta_wifi_mac_addr,
                                    expected_client_info, self.check_status_timeout)
        if self.errmsg:
            return

        logging.info("Perform Web authentication on the target station %s" % \
                     self.target_station.get_ip_addr())

        arg = tconfig.get_web_auth_params(self.zd, self.username, self.password)

        self.target_station.perform_web_auth(arg)

        logging.info("Try to ping to %s from the target station %s one more time" % \
                     (self.ip_addr, self.target_station.get_ip_addr()))

        self.errmsg = tmethod.client_ping_dest_is_allowed(
                          self.target_station,
                          self.ip_addr,
                          ping_timeout_ms = self.ping_timeout_ms)
        if self.errmsg:
            return

        # Verify information of the target station shown on the Zone Director one more time
        expected_status = 'Authorized'
        expected_user_info = self.username
        expected_client_info = {'ip': expected_user_info, 'status': expected_status}

        self.errmsg, sta_info = tmethod.verify_zd_client_status(
                                    self.zd, self.sta_wifi_mac_addr,
                                    expected_client_info, self.check_status_timeout)


    def _verifyGuestAccess(self):
        self._verifyStationConnection()
        if self.errmsg:
            return

        logging.info("Ping to %s from the target station" % self.ip_addr)
        self.errmsg = tmethod.client_ping_dest_not_allowed(
                          self.target_station,
                          self.ip_addr,
                          ping_timeout_ms = self.ping_timeout_ms)

        if self.errmsg:
            return

        # Verify information of the target station shown on the Zone Director
        expected_status = 'Unauthorized'
        expected_user_info = self.sta_wifi_ip_addr
        expected_client_info = {'ip': expected_user_info, 'status': expected_status}

        self.errmsg, sta_info = tmethod.verify_zd_client_status(
                                    self.zd, self.sta_wifi_mac_addr,
                                    expected_client_info, self.check_status_timeout)

        if self.errmsg:
            return

        logging.info("Perform Guest Pass authentication on the target station %s" % \
                     self.target_station.get_ip_addr())

        arg = tconfig.get_guest_auth_params(self.zd, self.guest_pass,
                                            self.use_tou, self.redirect_url)

        self.target_station.perform_guest_auth(arg)

        logging.info("Try to ping to %s from the target station %s one more time" % \
                     (self.ip_addr, self.target_station.get_ip_addr()))

        self.errmsg = tmethod.client_ping_dest_is_allowed(
                          self.target_station,
                          self.ip_addr,
                          ping_timeout_ms = self.ping_timeout_ms)

        if self.errmsg:
            return

        # Verify information of the target station shown on the Zone Director one more time
        expected_status = 'Authorized'
        expected_user_info = self.guest_name
        expected_client_info = {'ip': expected_user_info, 'status': expected_status}

        self.errmsg, sta_info = tmethod.verify_zd_client_status(
                                    self.zd, self.sta_wifi_mac_addr,
                                    expected_client_info, self.check_status_timeout)


    def _verifyStationConnection(self):
        """
        """
        logging.info("Configure a WLAN with SSID %s on the target station %s" % \
                     (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))
        self.target_station.cfg_wlan(self.wlan_cfg)

        logging.info("Make sure the station associates to the WLAN")
        start_time = time.time()
        while True:
            if self.target_station.get_current_status() == "connected":
                break

            time.sleep(self.sta_getstatus_interval)
            if time.time() - start_time > self.check_status_timeout:
                msg = "The station did not associate to the wireless network within %d \
                      seconds" % self.check_status_timeout
                raise Exception(msg)

        # TAK@20080214 -- get stations' wifi address
        anOK, self.sta_wifi_ip_addr, self.sta_wifi_mac_addr = \
            tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)

        if not anOK:
            self.errmsg = self.sta_wifi_mac_addr

        else:
            self.errmsg = ''

    #Cleanup
    def _cleanupTheZoneDirectorSetting(self):
        logging.info('Unblock all blocked clients')
        self.zd.unblock_clients('')

        logging.info("Remove all the WLANs on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)
        #lib.zd.aaa.remove_all_servers(self.zd)

        if self.conf['test_policy'] == 'guest access':
            logging.info("Remove all Guest Passes created on the Zone Director")
            self.zd.remove_all_guestpasses()

            if self.current_guest_access_policy:
                logging.info("Restore Guest Access Policy to original configuration on ZD")
                self.zd.set_guestaccess_policy(**self.current_guest_access_policy)

            if self.current_guest_pass_policy:
                logging.info("Restore Guest Password Policy to original configuration on ZD")
                self.zd.set_guestpass_policy(**self.current_guest_pass_policy)

