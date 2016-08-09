# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_EncryptionTypes_ZeroIT Test class tests the ability of a station to associate with
             an AP under ZD's control with a given security configuration provided in Zero-IT tool

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters: 'ip':'IP address to ping',
                    'target_station':'ip address of target station',
                    'wlan_cfg':'dictionary of association parameters',
                    'use_winxp_sta':'the bool value indicates whether platform of target station is XP or Vista'
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
       - Configure a WLAN on the ZD with given security setting.
       - On the wireless client, configure the Ethernet interface with an IP address that is in the same
         subnet with the ZD
       - Use a browser and access to the activation URL provided to download Zero-IT tool. Use the username
         and password given to pass authentication.
       - Execute the Zero-IT tool on the wireless client.
       - Verify if the client can access to the WLAN configured by Zero-IT tool.
       - Verify if the ZD shows correct information about the connected station.
       - Do a ping to make sure traffic gets forwarded.
       - Verify if the ZD shows correct information about the connected station.
   3. Cleanup:
       - Remove all wlan configuration on ZD.
       - Remove wireless profile on remote wireless STA

   How it is tested?
       - While the test is running, right after the local user is created on ZD, open another browser to ZD and
         remove that user. The script should report that Zero-IT tool cannot be downloaded because credential is invalid
       - Right after the Zero-IT tool is installed on the client, browse to ZD's WebUI and remove the WLAN. The script
         should report that it cannot connect to the WLAN.
"""

import os
import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

class ZD_EncryptionTypes_ZeroIT(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'ip':'IP address to ping',
                           'target_station':'ip address of target station',
                           'wlan_cfg':'dictionary of association parameters',
                           'use_winxp_sta':'the bool value indicates whether platform of target station is XP or Vista'}

    def config(self, conf):
        self._cfgInitTestParams(conf)

        self._cfgRemoveWlanOnZD()

        self._cfgGetTargetStation()

        self._cfgVerifyStationOS()

    def test(self):
        self._cfgCreateUserAndWlanOnZD()

        self._cfgConnectStationToWlan()

        if self.connected:
            self._cfgGetStaWifiIpAddress()

            self._testStationConnectivity()
            if self.errmsg: return ("FAIL", self.errmsg)
        else:
            self._testWlanInTheAir()
            if self.errmsg: return ("FAIL", self.errmsg)

        self._testVerifyStationInfoOnZD()
        if self.errmsg: return ("FAIL", self.errmsg)

        return ("PASS", "")

    def cleanup(self):
        logging.info("Remove all the WLANs on the Zone Director")
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        
        #self.zd.remove_all_cfg()

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
        self.conf = conf
        self.wlan_cfg = conf['wlan_cfg']
        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.target_ip = conf['ip']
        self.use_winxp_sta = conf['use_winxp_sta']

        self.zd = self.testbed.components['ZoneDirector']
        self.zd_ip_addr = self.zd.ip_addr
        self.sta_ip_addr = self.get_station_download_ip_addr()
        self.sta_net_mask = utils.get_subnet_mask(self.zd_ip_addr, False)
        self.activate_url = self.zd.get_zero_it_activate_url()

    def _cfgRemoveWlanOnZD(self):
        logging.info("Remove all non-default configuration on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

    def _cfgGetTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station'],
                                               self.testbed.components['Station'],
                                               check_status_timeout = self.check_status_timeout,
                                               remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgVerifyStationOS(self):
        logging.info("Verify the platform of the target station")
        if self.use_winxp_sta:
            if self.target_station.get_win_version() != "51":
                raise Exception("The Windows version of target station is not Windows XP")
        else:
            if self.target_station.get_win_version() != "60":
                raise Exception("The Windows version of target station is not Windows Vista")

    def _cfgCreateUserAndWlanOnZD(self):
        logging.info("Create a user on the ZD")
        self.zd.create_user(self.wlan_cfg['username'], self.wlan_cfg['password'])

        logging.info("Configure a WLAN with SSID %s on the Zone Director" % self.wlan_cfg['ssid'])
        self.zd.cfg_wlan(self.wlan_cfg)
        time.sleep(2)

    def _cfgConnectStationToWlan(self):
        logging.info("Using zero-it tool to configure a WLAN with SSID %s on the target station %s" % 
                     (self.wlan_cfg['ssid'], self.target_station.get_ip_addr()))
        self.target_station.cfg_wlan_with_zero_it(self.target_station.get_ip_addr(), self.sta_ip_addr,
                                                 self.sta_net_mask, self.wlan_cfg['auth'], self.wlan_cfg['use_radius'],
                                                 self.activate_url, self.wlan_cfg['username'], self.wlan_cfg['password'],
                                                 self.wlan_cfg['ssid'])

        logging.info("Verify the status of the wireless adapter on the target station")
        start_time = time.time()
        self.connected = True
        while True:
            if self.target_station.get_current_status() == "connected":
                break
            time.sleep(1)
            if time.time() - start_time > self.check_status_timeout:
                logging.info("Timed out. The station didn't associate to the WLAN after %s" % \
                             self.check_status_timeout)
                self.connected = False
                break

    def _cfgGetStaWifiIpAddress(self):
        # Renew the IP address of the wireless adapter on the wireless station
        res, val1, val2 = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)

        if not res:
            raise Exception(val2)

        self.sta_wifi_ip_addr = val1
        self.sta_wifi_mac_addr = val2.lower()

    def _testStationConnectivity(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.target_ip, ping_timeout_ms = self.ping_timeout * 1000)

    def _testWlanInTheAir(self):
        self.errmsg = tmethod.verify_wlan_in_the_air(self.target_station, self.wlan_cfg['ssid'])

    def _testVerifyStationInfoOnZD(self):
        logging.info("Verify information of the target station shown on the Zone Director")
        if self.wlan_cfg['auth'] == 'EAP':
            expected_ip = self.wlan_cfg['username']
        else:
            expected_ip = self.sta_wifi_ip_addr
        exp_client_info = {"ip": expected_ip, "status": "Authorized", "wlan": self.wlan_cfg['ssid']}

        self.errmsg, client_info = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_mac_addr, exp_client_info,
                                                        self.check_status_timeout)

    def get_station_download_ip_addr(self, vlan_id="301"):
        vlan_ip_table = self.testbed.components['L3Switch'].get_vlan_ip_table()
        ip_addr = [ ll['ip_addr'] for ll in vlan_ip_table if ll['vlan_id'] == vlan_id]
        return ".".join("".join(ip_addr).split(".")[:-1]) + ".50"

