"""
Description: ZD_Hotspot_Enable_Disable test class verifies the ability of the ZD to enable/disable Hotspot type
             of a WLAN

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: target_ip     : IP address of a available destination which is used to verify the connectivity
                                    of the wireless station
                    active_ap     : Symbolic name of the active AP - optional
                    target_station: IP address of target wireless station
                    hotspot_cfg   : Configuration of a Hotspot profile given as a dictionary, refer to the
                                    module hotspot_services_zd to find the configuration keys of a Hotspot profile
                                    The script verifies only keys that are specified in this dictionary structure
                    wlan_cfg      : Association parameters, given as a dictionary - optional
                    auth_info     : Information about the authentication method, given as a dictionary
                                    Refer to module aaa_servers_zd to find the keys to define a specific authentication server
                    acct_info     : Information about the accounting server, given as a dictionary - optional

   Result type: PASS/FAIL
   Results: PASS: target station can associate to the WLAN, ping to a destination successfully and
                  information is shown correctly in ZD
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
   2. Test:
       - Create the authentication server/accounting server/local user account on the ZD
       - Create the Hotspot profile with given configuration
       - Create a regular WLAN
       - Verify the status of the WLAN on the active AP and turn off the WLAN on other APs
       - Configure the wireless station to associate to the WLAN
       - Get the IP address of the wireless adapter on the wireless station
       - Verify the connectivity from the wireless station
       - Verify the status of the station on the ZD
       - Change the WLAN to a Hotspot WLAN
       - Configure the wireless station to associate to the WLAN again
       - Get the IP address of the wireless adapter on the wireless station again
       - Verify the connectivity from the wireless station before it is authenticated
       - Verify the status of the station on the ZD before it is authenticated
       - Perform Hotspot authentication on the wireless station
       - Verify the connectivity from the wireless station after it is authenticated
       - Verify the status of the station on the ZD after it is authenticated
   3. Cleanup:
       - Remove all configuration created on the ZD
       - Remove wireless profile on wireless station
"""

import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class ZD_Hotspot_Enable_Disable(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_ip': 'IP address to test connectivity',
                           'target_station': 'IP address of target station',
                           'active_ap': 'Symbolic name of the active AP - optional',
                           'hotspot_cfg': 'Configuration of a Hotspot profile given as a dictionary',
                           'wlan_cfg': 'Association parameters, given as a dictionary, optional',
                           'auth_info': 'Information about the authentication method, given as a dictionary'}

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgRemoveAllConfigOnZD()
        self._cfgGetTargetStation()
        self._cfgGetActiveAP()

    def test(self):
        self._cfgDefineAuthSourceOnZD()
        self._cfgCreateHotspotProfileOnZD()
        self._cfgCreateWlanOnZD()

        self._testVerifyWlanOnAPs()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._cfgAssociateStationToWlan()
        self._cfgGetStaWifiIpAddress()
        self._testStationConnectivity()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._testVerifyStationInfoOnZD()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._cfgModifyWlanOnZD()

        self._testVerifyWlanOnAPs()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._cfgAssociateStationToWlan()
        self._cfgGetStaWifiIpAddress()
        self._testStationConnectivityBeforeHotspotAuth()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testVerifyStationInfoOnZDBeforeHotspotAuth()
        if self.errmsg: return ("FAIL", self.errmsg)

        self._cfgPerformHotspotAuthOnStation()

        self._testStationConnectivityAfterHotspotAuth()
        if self.errmsg: return ("FAIL", self.errmsg)
        self._testVerifyStationInfoOnZDAfterHotspotAuth()
        if self.errmsg: return ("FAIL", self.errmsg)

        return ("PASS", "The ZD could configure the WLAN to disable/enable Hotspot service properly")

    def cleanup(self):
        self._cfgRemoveAllConfigOnZDAtCleanup()
        self._cfgRemoveWlanFromStation()

#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(ping_timeout_ms = 10000,
                         check_status_timeout = 90,
                         check_wlan_timeout = 45)
        self.conf.update(conf)

        if not self.conf.has_key('wlan_cfg'):
            # Obtain the default open system configuration
            self.conf['wlan_cfg'] = tmethod8.get_default_wlan_cfg()
        self.conf['wlan_cfg']['ssid'] = tmethod.touch_ssid("WISPr-WLAN-UNDER-TEST")

        # Hotspot configuration must be provided
        if not self.conf.has_key('hotspot_cfg'):
            raise Exception('Hotspot configuration was not given')

        # Give it a name if not given
        if not self.conf['hotspot_cfg'].has_key('name'):
            self.conf['hotspot_cfg']['name'] = "WISPr Profile Under Test"

        # Auth information must be provided
        if not self.conf.has_key('auth_info'):
            raise Exception('Authentication configuration was not given')

        # Give the auth server a name, and assign it to the hotspot profile
        if self.conf['auth_info']['type'] != "local":
            self.conf['auth_info']['svr_name'] = "Authentication Server"
            self.conf['hotspot_cfg']['auth_svr'] = self.conf['auth_info']['svr_name']
        else:
            # If there is not any auth server, the local database is used
            self.conf['hotspot_cfg']['auth_svr'] = "Local Database"

        # Give the accounting server a name, and assign it to the hotspot profile
        if self.conf.has_key('acct_info'):
            self.conf['acct_info']['svr_name'] = "Accouting Server"
            self.conf['hotspot_cfg']['acct_svr'] = self.conf['acct_info']['svr_name']

        self.zd = self.testbed.components['ZoneDirector']

        self.errmsg = ''

    def _cfgRemoveAllConfigOnZD(self):
        logging.info("Remove all configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        #lib.zd.wispr.remove_all_profiles(self.zd)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

    def _cfgGetTargetStation(self):
        logging.info("Find the target station on the test bed")
        self.target_station = tconfig.get_target_station(self.conf['target_station'],
                                                       self.testbed.components['Station'],
                                                       check_status_timeout = self.conf['check_status_timeout'],
                                                       remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgGetActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in the test bed" % self.conf['active_ap'])

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
        logging.info("Create a Hotspot profile on the ZoneDirector")
        lib.zd.wispr.create_profile(self.zd, **self.conf['hotspot_cfg'])

    def _cfgCreateWlanOnZD(self):
        logging.info("Create WLAN [%s] as a standard WLAN on the Zone Director" % self.conf['wlan_cfg']['ssid'])
        lib.zd.wlan.create_wlan(self.zd, self.conf['wlan_cfg'])
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")

    def _testVerifyWlanOnAPs(self):
        if self.conf.has_key('active_ap'):
            self.errmsg = tmethod.verify_wlan_on_aps(self.active_ap, self.conf['wlan_cfg']['ssid'], self.testbed.components['AP'])

    def _cfgAssociateStationToWlan(self):
        tmethod.assoc_station_with_ssid(self.target_station, self.conf['wlan_cfg'], self.conf['check_status_timeout'])

    def _cfgGetStaWifiIpAddress(self):
        res, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
        if not res:
            raise Exception(val2)
        self.sta_wifi_if = {'ip': val1, 'mac': val2.lower()}

    def _testStationConnectivity(self):
        logging.info("Verify the connectivity from the station when associating to a standard WLAN")
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.conf['target_ip'],
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])

    def _testVerifyStationInfoOnZD(self):
        logging.info("Verify information of the target station shown on the Zone Director")
        exp_client_info = {"ip": self.sta_wifi_if['ip'], "status": "Authorized", "wlan": self.conf['wlan_cfg']['ssid']}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_if['mac'],
                                                                           exp_client_info, self.conf['check_status_timeout'])

    def _cfgModifyWlanOnZD(self):
        logging.info("Modify the WLAN [%s] to be a Hotspot WLAN on the Zone Director" % self.conf['wlan_cfg']['ssid'])
        hotspot_wlan_cfg = {'type': 'hotspot', 'hotspot_profile':self.conf['hotspot_cfg']['name']}
        lib.zd.wlan.edit_wlan(self.zd, self.conf['wlan_cfg']['ssid'], hotspot_wlan_cfg)
        tmethod8.pause_test_for(3, "Wait for the ZD to push new configuration to the APs")

    def _testStationConnectivityBeforeHotspotAuth(self):
        logging.info("Verify the connectivity from the station before Hotspot authentication is performed")
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.conf['target_ip'],
                                                           ping_timeout_ms = self.conf['ping_timeout_ms'])

    def _testVerifyStationInfoOnZDBeforeHotspotAuth(self):
        logging.info("Verify information of the target station shown on the Zone Director before performing Hotspot authentication")
        exp_client_info = {"ip": self.sta_wifi_if['ip'], "status": "Unauthorized", "wlan": self.conf['wlan_cfg']['ssid']}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_if['mac'],
                                                                           exp_client_info, self.conf['check_status_timeout'])

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


    def _testStationConnectivityAfterHotspotAuth(self):
        logging.info("Verify the connectivity from the station after Hotspot authentication is performed")
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.conf['target_ip'],
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])

    def _testVerifyStationInfoOnZDAfterHotspotAuth(self):
        logging.info("Verify information of the target station shown on the Zone Director after performing Hotspot authentication")
        exp_client_info = {"ip": self.conf['auth_info']['username'], "status": "Authorized", "wlan": self.conf['wlan_cfg']['ssid']}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_if['mac'],
                                                                           exp_client_info, self.conf['check_status_timeout'])
#
# cleanup()
#
    def _cfgRemoveAllConfigOnZDAtCleanup(self):
        logging.info("Remove all WLANs configured on the ZD")
        lib.zd.wlan.delete_all_wlans(self.zd)
        logging.info("Remove all HOTSPOT profiles configured on the ZD")
        lib.zd.wispr.remove_all_profiles(self.zd)
        logging.info("Remove all AAA servers configured on the ZD")
        lib.zd.aaa.remove_all_servers(self.zd)

    def _cfgRemoveWlanFromStation(self):
        if self.target_station:
            logging.info("Remove all WLANs from the station")
            tconfig.remove_all_wlan_from_station(self.target_station, check_status_timeout = self.conf['check_status_timeout'])

