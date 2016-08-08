"""
Description: ZD_Hotspot_Multiple_Profile_Wlan test class verifies the ability of the ZD to deploy multiple Hotspot
             WLANs using multiple or single Hotspot profile

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: target_ip       : IP address of a available destination which is used to verify the connectivity
                                      of the wireless station
                    target_station  : IP address of target wireless station
                    hotspot_cfg     : Configuration of a Hotspot profile given as a dictionary, refer to the
                                      module hotspot_services_zd to find the configuration keys of a Hotspot profile
                    number_of_wlan  : Number of the WLANs will be created and verified
                    testing_feature : "single_profile" or "multiple_profile"

   Result type: PASS/FAIL
   Results: PASS: target station can associate to the WLAN, ping to a destination successfully and
                  information is shown correctly in ZD
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration about WLANs, users, authentication servers, and active clients on the ZD
       - Generate different WLAN configuration and Hotspot configuration depending on the test required
   2. Test:
       - Create the authentication source on the ZD
       - Create the Hotspot profiles
       - Create a Hotspot WLANs
       - For each WLAN created, perform the steps below:
           - Configure the wireless station to associate to the Hotspot WLAN
           - Get the IP address of the wireless adapter on the wireless station
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
import re
import time
import random

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import Ratutils as utils

class ZD_Hotspot_Multiple_Profile_Wlan(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'target_ip': 'IP address to test connectivity',
                           'target_station': 'IP address of target station',
                           'hotspot_cfg': 'Hotspot profile configuration',
                           'testing_feature': 'multiple_profile/single_profile',
                           'number_of_wlan': 'Number of Hotspot WLAN will be created and verified'}

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgRemoveAllConfigOnZD()
        self._cfgGetTargetStation()

    def test(self):
        self._cfgDefineAuthSourceOnZD()
        self._cfgCreateHotspotProfilesOnZD()
        self._cfgCreateWlansOnZD()

        for wlan_idx in range(self.conf['number_of_wlan']):
            wlan_cfg = self.conf['wlan_cfg_list'][wlan_idx]
            logging.info("Verify the deployment of WLAN [%s] using Hotspot profile [%s]" % \
                         (wlan_cfg['ssid'], wlan_cfg['hotspot_profile']))

            self._cfgAssociateStationToWlan(wlan_idx)
            self._cfgGetStaWifiIpAddress()

            self._testVerifyStationInfoOnZDBeforeHotspotAuth(wlan_idx)
            if self.errmsg: return ("FAIL", self.errmsg)
            self._testStationConnectivityBeforeHotspotAuth()
            if self.errmsg: return ("FAIL", self.errmsg)

            hotspot_profile_idx = 0 if self.conf['testing_feature'] == "single_profile" else wlan_idx
            self._cfgPerformHotspotAuthOnStation(hotspot_profile_idx)

            self._testVerifyStationInfoOnZDAfterHotspotAuth(wlan_idx)
            if self.errmsg: return ("FAIL", self.errmsg)
            self._testStationConnectivityAfterHotspotAuth()
            if self.errmsg: return ("FAIL", self.errmsg)

            self._cfgDeleteStationFromZD()
            self._cfgRemoveWlanFromStation()

            self.msg += "The WLAN [%s] with Hotspot profile [%s] was configured and deployed properly. " % \
                        (wlan_cfg['ssid'], wlan_cfg['hotspot_profile'])

        return ("PASS", self.msg.strip())

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

        self.target_station = None
        self.zd = self.testbed.components['ZoneDirector']

        # Current limitation of the script, only verify up to 6 WLAN
        if self.conf['number_of_wlan'] > 6:
            logging.info("WARNING: The script supports verifying maximum 6 WLANs")
            self.conf['number_of_wlan'] = 6

        # Define the WLAN configuration set
        self._cfgGenWlanCfg()
        # Make sure there are enough WLAN config to create the Hotspot WLAN
        idx = 0
        while len(self.conf['wlan_cfg_list']) < self.conf['number_of_wlan']:
            new_wlan_cfg = self.conf['wlan_cfg_list'][idx].copy()
            self.conf['wlan_cfg_list'].append(new_wlan_cfg)
            idx += 1
        # Update the name and type
        for wlan_cfg in self.conf['wlan_cfg_list']:
            wlan_cfg['ssid'] = "%s-%06d" % (wlan_cfg['ssid'], random.randrange(1, 999999))
            wlan_cfg['type'] = "hotspot"

        # Hotspot configuration must be provided
        if not self.conf.has_key('hotspot_cfg'):
            raise Exception('Hotspot configuration was not given')
        # Give it a name if not given
        if not self.conf['hotspot_cfg'].has_key('name'):
            self.conf['hotspot_cfg']['name'] = "WISPr Profile Under Test"

        # Define the Hotspot configuration list
        self.conf['hotspot_cfg_list'] = []
        if self.conf['testing_feature'] == "single_profile":
            self.conf['hotspot_cfg_list'].append(self.conf['hotspot_cfg'])
            for idx in range(self.conf['number_of_wlan']):
                self.conf['wlan_cfg_list'][idx]['hotspot_profile'] = self.conf['hotspot_cfg_list'][0]['name']
        elif self.conf['testing_feature'] == "multiple_profile":
            for idx in range(self.conf['number_of_wlan']):
                cfg = self.conf['hotspot_cfg'].copy()
                cfg['name'] = "%s-%d" % (cfg['name'], idx)
                self.conf['hotspot_cfg_list'].append(cfg)
                self.conf['wlan_cfg_list'][idx]['hotspot_profile'] = self.conf['hotspot_cfg_list'][idx]['name']

        # Using local authentication source
        self.conf['auth_info'] = {'type': 'local', 'username': 'local.username', 'password': 'local.password'}
        for cfg in self.conf['hotspot_cfg_list']:
            cfg['auth_svr'] = "Local Database"

        self.errmsg = ""
        self.msg = ""
        self.wlan_id = None

    def _cfgGenWlanCfg(self):
        wlan_cfg_list = []
        # Open-None
        wlan_cfg_list.append(dict(ssid = "RAT-Open-None", auth = "open", encryption = "none"))
        # Open-WEP64
        wlan_cfg_list.append(dict(ssid = "RAT-Open-WEP64", auth = "open", encryption = "WEP-64",
                             key_index = "1", key_string = utils.make_random_string(10, "hex")))
        # Open-WEP128
        wlan_cfg_list.append(dict(ssid = "RAT-Open-WEP128", auth = "open", encryption = "WEP-128",
                             key_index = "1", key_string = utils.make_random_string(26, "hex")))
        # WPA-PSK-TKIP
        wlan_cfg_list.append(dict(ssid = "RAT-WPA-PSK-TKIP", auth = "PSK", wpa_ver = "WPA" , encryption = "TKIP",
                             key_string = utils.make_random_string(random.randint(8, 63), "hex")))
        # WPA-PSK-AES
        wlan_cfg_list.append(dict(ssid = "RAT-WPA-PSK-AES", auth = "PSK", wpa_ver = "WPA" , encryption = "AES",
                             key_string = utils.make_random_string(random.randint(8, 63), "hex")))
        # WPA2-PSK-TKIP
        wlan_cfg_list.append(dict(ssid = "RAT-WPA2-PSK-TKIP", auth = "PSK", wpa_ver = "WPA2" , encryption = "TKIP",
                             key_string = utils.make_random_string(random.randint(8, 63), "hex")))
        # WPA2-PSK-AES
        wlan_cfg_list.append(dict(ssid = "RAT-WPA2-PSK-AES", auth = "PSK", wpa_ver = "WPA2" , encryption = "AES",
                             key_string = utils.make_random_string(random.randint(8, 63), "hex")))

        self.conf['wlan_cfg_list'] = wlan_cfg_list

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

#
# test()
#
    def _cfgDefineAuthSourceOnZD(self):
        logging.info("Create a user account on the ZoneDirector")
        self.zd.create_user(self.conf['auth_info']['username'], self.conf['auth_info']['password'])

    def _cfgCreateHotspotProfilesOnZD(self):
        for hotspot_cfg in self.conf['hotspot_cfg_list']:
            logging.info("Create the Hotspot profile [%s] on the ZoneDirector" % hotspot_cfg['name'])
            lib.zd.wispr.create_profile(self.zd, **hotspot_cfg)

    def _cfgCreateWlansOnZD(self):
        for idx in range(self.conf['number_of_wlan']):
            logging.info("Create WLAN [%s] as a Hotspot WLAN on the Zone Director" % self.conf['wlan_cfg_list'][idx]['ssid'])
            lib.zd.wlan.create_wlan(self.zd, self.conf['wlan_cfg_list'][idx])
        tmethod8.pause_test_for(10, "Wait for the ZD to push new configuration to the APs")

    def _cfgAssociateStationToWlan(self, wlan_idx):
        tmethod.assoc_station_with_ssid(self.target_station, self.conf['wlan_cfg_list'][wlan_idx], self.conf['check_status_timeout'])

    def _cfgGetStaWifiIpAddress(self):
        res, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.conf['check_status_timeout'])
        if not res:
            raise Exception(val2)
        self.sta_wifi_if = {'ip': val1, 'mac': val2.lower()}

    def _testStationConnectivityBeforeHotspotAuth(self):
        logging.info("Verify the connectivity from the station before Hotspot authentication is performed")
        self.errmsg = tmethod.client_ping_dest_not_allowed(self.target_station, self.conf['target_ip'],
                                                           ping_timeout_ms = self.conf['ping_timeout_ms'])
        if self.errmsg: return

    def _testVerifyStationInfoOnZDBeforeHotspotAuth(self, wlan_idx):
        logging.info("Verify information of the target station shown on the Zone Director before performing Hotspot authentication")
        exp_client_info = {"ip": self.sta_wifi_if['ip'], "status": "Unauthorized", "wlan": self.conf['wlan_cfg_list'][wlan_idx]['ssid']}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_if['mac'],
                                                                           exp_client_info, self.conf['check_status_timeout'])

    def _cfgPerformHotspotAuthOnStation(self, idx):
        logging.info("Perform Hotspot authentication on the station")
        if self.conf['hotspot_cfg_list'][idx].has_key('start_page'):
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
        logging.info("The not restricted destination: %s" % self.conf['target_ip'])
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.conf['target_ip'],
                                                          ping_timeout_ms = self.conf['ping_timeout_ms'])

    def _testVerifyStationInfoOnZDAfterHotspotAuth(self, wlan_idx):
        logging.info("Verify information of the target station shown on the Zone Director after performing Hotspot authentication")
        exp_client_info = {"ip": self.conf['auth_info']['username'], "status": "Authorized", "wlan": self.conf['wlan_cfg_list'][wlan_idx]['ssid']}

        self.errmsg, self.client_info_on_zd = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_if['mac'],
                                                                           exp_client_info, self.conf['check_status_timeout'])

    def _cfgDeleteStationFromZD(self):
        logging.info("Remove the session of the station from the ZD")
        self.zd.delete_clients(self.sta_wifi_if['mac'])

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

