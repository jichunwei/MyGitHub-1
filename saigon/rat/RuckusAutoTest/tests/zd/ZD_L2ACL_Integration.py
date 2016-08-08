# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script support to verify the L2 ACL testing in combination with Client Isolation, Web Authen tication, Vlan or Tunnel.
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
            'target_station': the target station IP address
            'active_ap': the symbolic name of the active ap
            'testcase': the testcase description. Ex: 'with-isolation', 'with-web-authentication'

   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
        - Clean up the testing environment by remove all non default configuration on ZD,
        target station, and active AP.

        - Create an WLAN that have the appropriation option:
              + If testcase is 'with-isolation': enable the Client Isolation option
              + If testcase is 'with-web-authentication': enable the Web Authentication option
              + If testcase is 'with-vlan': enable the VLAN with the vlan id
              + If testcase is 'with-tunnel': enable the Tunnel option

   2. Test:
        - Create an ACL policy (allow access)

   3. Cleanup:
        - Clean up the testing environment by remove all non default configuration on ZD,
        target station, and active AP.


   How it is tested?

"""

import logging
import time
from copy import deepcopy
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class ZD_L2ACL_Integration(Test):
    required_components = []
    test_parameters = {}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cfgZoneDirector()
        self._cfgActiveAP()
        self._cfgTargetStation()

    def test(self):
        self._createL2ACLToTest()

        self._createWLANForTest()
        self._remove_all_wlanOnNonActiveAPs()
        # Apply the deny access ACL policy to WLAN
        self._applyL2ACLToWLAN(self.test_wlan_conf['ssid'], self.deny_l2acl_conf['acl_name'])
        # Verify the station could not access to the network
        self._testVerifyStationAssociation(self.test_wlan_conf, False)
        if self.errmsg:
            return ('FAIL', self.errmsg)

        # Apply the allow access ACL policy to WLAN
        self._applyL2ACLToWLAN(self.test_wlan_conf['ssid'], self.allow_l2acl_conf['acl_name'])
        # Verify the station could access to the network and the combination feature works well
        test_function = {'with-isolation': self._testVerifyIsolationFunctionality,
                         'with-web-authentication': self._testVerifyWebAuthenticationFunctionality,
                         'with-vlan': self._testVerifyVLANFunctionality,
                         'with-tunnel': self._testVerifyTunnelFunctionality,
                         'with-mac-authentication':self._testMACAuthenticatonFunctionality
                         }[self.testcase]
        test_function()
        if self.errmsg:
            return ('FAIL', self.errmsg)

        logging.info(self.passmsg)
        return ('PASS', self.passmsg)

    def cleanup(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        # Remove all wlan profiles on target station
        if self.target_station:
            self.target_station.remove_all_wlan()

    # Configuration
    def _initTestParameters(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap = None
        self.target_station = None

        self.test_wlan_conf = {'ssid':'Testing WLAN', 'auth':'open', 'encryption':'none'}
        self.allow_l2acl_conf = {'acl_name':'Allow Access ACL', 'description': '', 'allowed_access': True, 'mac_entries': []}
        self.deny_l2acl_conf = {'acl_name':'Deny Access ACL', 'description': '', 'allowed_access': False, 'mac_entries': []}

        self.check_status_timeout = 180
        self.negative_check_status_timeout = 20
        self.break_time = 2

        self.errmsg = ''
        self.passmsg = ''
        self.username = 'testuser'
        self.password = 'testpass'
        self.testcase = self.conf['testcase']

        tmp_list = self.conf['dest_ip'].split('/')
        self.dest_ip = tmp_list[0]
        if len(tmp_list) == 2:
            self.expected_subnet_mask = tmp_list[1]
        else:
            self.expected_subnet_mask = ''

    def _cfgZoneDirector(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

        if self.testcase == 'with-web-authentication':
            # Create user for authentication
            self.zd.create_user(self.username, self.password)

        if self.testcase == 'with-mac-authentication':
            self._cfgTheAuthenServerOnZD()

    def _cfgActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])
            self.active_ap_mac = self.active_ap.base_mac_addr.lower()

    def _remove_all_wlanOnNonActiveAPs(self):
        if self.active_ap:
            for ap in self.testbed.components['AP']:
                if ap is not self.active_ap:
                    logging.info("Remove all WLAN on non-active AP %s" % ap.ip_addr)
                    ap.remove_all_wlan()

            logging.info("Verify WLAN status on the active AP %s" % self.active_ap.ip_addr)
            if not self.active_ap.verify_wlan():
                raise Exception('Not all WLAN are up on active AP %s' % self.active_ap.ip_addr)

    def _cfgTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                                                           , self.testbed.components['Station']
                                                           , check_status_timeout = self.check_status_timeout
                                                           , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

        # Get mac address of wireless adapter on the target station.
        # This address is used as the restricted mac address in an ACL rule
        sta_wifi_ip_addr = None
        self.sta_wifi_mac_addr = None
        try:
            sta_wifi_ip_addr, self.sta_wifi_mac_addr = self.target_station.get_wifi_addresses()
        except:
            raise Exception("Unable to get MAC address of the wireless adapter of the target station %s" % 
                            self.target_station.get_ip_addr())

    def _cfgTheAuthenServerOnZD(self):
        logging.info('Configure the external server on Zone Director')
        lib.zd.aaa.create_server(self.zd, **self.conf['auth_server_info'])

    # Testing
    def _createL2ACLToTest(self):
        self.allow_l2acl_conf.update({'mac_list': [self.sta_wifi_mac_addr]})
        lib.zd.ac.create_l2_acl_policy(self.zd, self.allow_l2acl_conf)
        self.deny_l2acl_conf.update({'mac_list': [self.sta_wifi_mac_addr]})
        lib.zd.ac.create_l2_acl_policy(self.zd, self.deny_l2acl_conf)

    def _createWLANForTest(self):
        if self.testcase == 'with-isolation':
            self.test_wlan_conf.update({'do_isolation': True})
            logging.info('Create the test WLAN with Client Isolation is enabled')
        elif self.testcase == 'with-web-authentication':
            self.test_wlan_conf.update({'do_webauth': True})
            logging.info('Create the test WLAN with Web Authentication is enabled')
        elif self.testcase == 'with-vlan':
            self.test_wlan_conf.update({'vlan_id': self.conf['vlan_id']})
            logging.info('Create the test WLAN with vlan is enabled')
        elif self.testcase == 'with-tunnel':
            self.test_wlan_conf.update({'do_tunnel': True})
            logging.info('Create the test WLAN with tunnel is enabled')
        elif self.testcase == 'with-mac-authentication':
            self.test_wlan_conf.update({'auth':'mac'})
            logging.info('Create the test WLAN with authentication mode is MAC Authentication')

        lib.zd.wlan.create_wlan(self.zd, self.test_wlan_conf)

    def _applyL2ACLToWLAN(self, wlan_name, acl_name):
        lib.zd.wlan.edit_wlan(self.zd, wlan_name, {'acl_name': acl_name})

    def _testVerifyStationAssociation(self, wlan_conf, allow_access = True):
        check_status_timeout = self.check_status_timeout if allow_access else self.negative_check_status_timeout

        errmsg = tmethod.assoc_station_with_ssid(self.target_station, wlan_conf, check_status_timeout)
        if errmsg and not allow_access:
            msg = '[Correct Behavior]: Station [%s] is not allowed and %s' % (self.sta_wifi_mac_addr, errmsg)
        elif errmsg and allow_access:
            msg = '[Incorrect Behavior]: Station [%s] is allowed but %s' % (self.sta_wifi_mac_addr, errmsg)
            self.errmsg = msg
        elif not errmsg and not allow_access:
            msg = '[Incorrect Behavior]: Station [%s] is not allowed but still connected to WLAN "%s" successfully'
            msg = msg % (self.sta_wifi_mac_addr, wlan_conf['ssid'])
            self.errmsg = msg
        elif not errmsg and allow_access:
            msg = '[Correct Behavior]: Station [%s] is allowed and connected to WLAN "%s" successfully'
            msg = msg % (self.sta_wifi_mac_addr, wlan_conf['ssid'])
        else:
            msg = ''

        logging.info(msg)

    def _testVerifyIsolationFunctionality(self):
        self._testVerifyStationAssociation(self.test_wlan_conf, True)
        if self.errmsg: return

        val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)
        if not val:
            raise Exception(val2)
        else:
            sta_wifi_ip_addr = val1

        logging.info('Verify if target station could ping to an IP in same subnet')
        errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.dest_ip)
        if errmsg:
            msg = '[Incorrect Behavior] %s while Wireless Client Isolation is enabled on wlan "%s"'
            msg = errmsg % (errmsg, self.test_wlan_conf['ssid'])
            self.errmsg = msg
            logging.info(self.errmsg)
            return
        else:
            msg = '[Correct Behavior]: Target station "%s" could not ping "%s"'
            msg = msg % (sta_wifi_ip_addr, self.dest_ip)
            logging.info(msg)

        self.passmsg = 'The ACL Policy works well on WLAN with "Wireless Client Isolation" enabled'

    def _testVerifyWebAuthenticationFunctionality(self):
        self._testVerifyStationAssociation(self.test_wlan_conf, True)
        if self.errmsg: return

        val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)
        if not val:
            raise Exception(val2)
        sta_wifi_ip_addr = val1
        sta_wifi_mac_addr = val2

        self.errmsg, client_info = tmethod.verify_zd_client_is_unauthorized(self.zd, sta_wifi_ip_addr, sta_wifi_mac_addr,
                                                                       self.check_status_timeout)
        if self.errmsg: return

        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.dest_ip)
        if self.errmsg: return

        logging.info("Perform Web Authentication on the target station %s" % self.conf['target_station'])
        arg = tconfig.get_web_auth_params(self.zd, self.username, self.password)
        self.target_station.perform_web_auth(arg)

        self.errmsg, client_info = tmethod.verify_zd_client_is_authorized(self.zd, self.username, sta_wifi_mac_addr,
                                                                     self.check_status_timeout)
        if self.errmsg: return

        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.dest_ip)
        if self.errmsg: return

        self.passmsg = 'The ACL Policy works well on WLAN with "Web Authentication" enabled'

    def _testVerifyVLANFunctionality(self):
        self._testVerifyStationAssociation(self.test_wlan_conf, True)
        if self.errmsg: return

        val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)
        if not val:
            raise Exception(val2)
        sta_wifi_ip_addr = val1
        sta_wifi_mac_addr = val2

        # Verify if vlan then client and target server should be same subnet
        self._testVerifyClientAndDestAtSameSubnet(sta_wifi_ip_addr)
        if self.errmsg:
            logging.info(self.errmsg)
            return

        self.passmsg = 'The ACL Policy works well on WLAN with VLAN enabled'

    def _testVerifyTunnelFunctionality(self):
        self._testVerifyStationAssociation(self.test_wlan_conf, True)
        if self.errmsg: return

        val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)
        if not val:
            raise Exception(val2)
        sta_wifi_ip_addr = val1
        sta_wifi_mac_addr = val2

        # Verify if tunnel mode enabled the station mac address should be in tunnel mode
        self._testVerifyStationMacInTunnelMode(sta_wifi_mac_addr)
        if self.errmsg:
            logging.info(self.errmsg)
            return

        self.passmsg = 'The ACL Policy works well on WLAN with Tunnel mode enabled'

    def _testVerifyClientAndDestAtSameSubnet(self, sta_wifi_ip_addr):
        # Check if the wireless IP address of the station belongs to the subnet of the parameter 'ip'.
        sta_wifi_subnet = utils.get_network_address(sta_wifi_ip_addr, self.expected_subnet_mask)
        expected_subnet = utils.get_network_address(self.dest_ip, self.expected_subnet_mask)
        if sta_wifi_subnet != expected_subnet:
            errmsg = "The wireless IP address '%s' of target station %s has different subnet with '%s'"
            self.errmsg = errmsg % (sta_wifi_ip_addr, self.target_station.get_ip_addr(), self.dest_ip)

    def _testVerifyStationMacInTunnelMode(self, sta_wifi_mac_addr):
        if self.active_ap:
            ap_mac = self.active_ap.get_base_mac().lower()
        else:
            ap_mac = tmethod.get_active_client_by_mac_addr(sta_wifi_mac_addr, self.zd)['apmac'].lower()
        sta_mac = sta_wifi_mac_addr.lower()

        self.errmsg = self.testbed.verify_station_mac_in_tunnel_mode(ap_mac, sta_mac, True)

    def _testMACAuthenticatonFunctionality(self):
        self._testVerifyStationAssociation(self.test_wlan_conf, True)
        if self.errmsg: return

        val, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)
        if not val:
            raise Exception(val2)
        sta_wifi_ip_addr = val1
        sta_wifi_mac_addr = val2

        self.errmsg, client_info = tmethod.verify_zd_client_is_authorized(self.zd, sta_wifi_ip_addr, sta_wifi_mac_addr,
                                                                     self.check_status_timeout)
        if self.errmsg:#chen.tao 2014-2-24, to fix ZF-7570
            tmp_mac_addr = deepcopy(sta_wifi_mac_addr)
            self.errmsg, client_info = tmethod.verify_zd_client_is_authorized(
                                           self.zd,''.join(tmp_mac_addr.split(':')).lower(),
                                           sta_wifi_mac_addr,
                                           self.check_status_timeout)

        if self.errmsg: return

        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.dest_ip)
        if self.errmsg: return

        self.passmsg = 'The ACL Policy works well on a "MAC Authentication" WLAN'

    # Clean up

