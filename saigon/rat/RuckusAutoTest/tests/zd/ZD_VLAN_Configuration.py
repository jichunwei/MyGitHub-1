# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: ZD_VLAN_Configuration Test class tests the ability of the Zone Director to deploy WLAN with VLAN tagging
             to wireless station

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'ZoneDirector'
   Test parameters: 'ip': 'IP address to ping. Must be given in format n.n.n.n/m.m.m.m',
                    'vlan_id': 'A VLAN ID to assign to the WLAN',
                    'use_valid_id': 'A boolean value to indiate the validity of the VLAN ID',
                    'target_station': 'IP address of target station'
                    'active_ap': 'MAC address of the active AP; optional'
   Result type: PASS/FAIL/ERROR
   Results: PASS: target station can associate, pass WebAuth, ping to a destination successfully and
                  information is shown correctly in ZD and AP
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Remove all WLAN configuration on the target station
       - Remove all configuration on the Zone Director
   2. Test:
       - Configure a WLAN on the ZD with open security setting
       - Configure the WLAN to tag traffic with given VLAN ID
       - Verify if the ZD allows/disallows to use the VLAN ID if it is valid/invalid
       - Configure the wireless client to associate to the WLAN above
       - Get IP and MAC address of the wireless adapter on the wireless client
       - Verify if the IP address is in the same subnet with the given IP address (address to ping)
       - Verify if the wireless client can perform a ping to that address
       - Verify information about the wireless client shown on ZD
   3. Cleanup:
       - Remove wireless profile on remote wireless STA
       - Remove all configuration on the ZD

   How it is tested?
       - After the client has associated to the WLAN successfully, log on the wireless client and disconnect the
         connection. The script must report that the ping to destination could not be done.
"""

import os
import re
import logging
import time

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class ZD_VLAN_Configuration(Test):
    required_components = ['Station', 'ZoneDirector']
    parameter_description = {'ip': 'IP address to ping. Must be given in format n.n.n.n/m.m.m.m',
                           'vlan_id': 'A VLAN ID to assign to the WLAN',
                           'use_valid_id': 'A boolean value to indiate the validity of the VLAN ID',
                           'target_station': 'IP address of target station',
                           'active_ap': 'MAC address of the active AP'}

    def config(self, conf):
        # Define test parameters
        self._cfgInitTestParams(conf)

        # Find the target station object and remove all Wlan profiles
        self._cfgGetTargetStation()

        # Remove all configuration on the ZD
        self._cfgRemoveWlanOnZD()

    def test(self):
        # Try to create a WLAN and assign a VLAN ID to it
        self._testCreateWlanOnZoneDirector()
        if self.errmsg: return ("FAIL", self.errmsg)

        if not self.is_id_valid:
            return ("PASS", "The ZD didn't allow to use VLAN ID [%s]" % self.conf["vlan_id"])

        # If requested, detect the active AP object remove the WLAN on all non-active APs
        self._cfgGetActiveAP()

        # Try to connect the wireless station to the configured WLAN
        self._testStationAssocWithSSID()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Get the IP address assigned to the wireless adapter on the wireless station
        self._testRenewWifiIpAddress()

        # Verify the assigned IP address
        self._testIPAddressAssignment()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Verify the connectivity
        self._testStationConnectivity()
        if self.errmsg: return ("FAIL", self.errmsg)

        # Verify information shown on the ZD
        self._testVerifyStationInfoOnZD()
        if self.errmsg: return ("FAIL", self.errmsg)

        return ("PASS", "VLAN ID [%s] was configured and deployed successfully" % self.wlan_cfg['vlan_id'])

    def cleanup(self):
        logging.info("Remove all the WLANs on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

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
        self.is_id_valid = conf['use_valid_id']
        self.wlan_cfg = {'username': '', 'sta_auth': 'open', 'ras_port': '', 'key_index': '', 'auth': 'open',
                         'sta_encryption': 'none', 'ras_addr': '', 'password': '', 'ad_domain': '', 'ad_port': '',
                         'ssid': 'rat-vlan-config-%s' % conf['vlan_id'], 'key_string': '', 'sta_wpa_ver': '',
                         'wpa_ver': '', 'encryption': 'none', 'ad_addr': '', 'ras_secret': '',
                         'vlan_id': conf['vlan_id']}
        self.ping_timeout = 150
        self.check_status_timeout = 120
        self.zd = self.testbed.components['ZoneDirector']

        tmp_list = conf['ip'].split("/")
        self.ip_addr = tmp_list[0]
        if len(tmp_list) == 2:
            self.mask = tmp_list[1]
        else:
            # If subnet mask is not given then use the default mask
            self.mask = ""

    def _cfgGetActiveAP(self):
        # Find the Active AP and disable all non-mesh WLAN interfaces on the other APs
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])

    def _cfgGetTargetStation(self):
        self.target_station = tconfig.get_target_station(self.conf['target_station']
                              , self.testbed.components['Station']
                              , check_status_timeout = self.check_status_timeout
                              , remove_all_wlan = True)
        if not self.target_station:
            raise Exception("Target station %s not found" % self.conf['target_station'])

    def _cfgRemoveWlanOnZD(self):
        logging.info("Remove all WLAN on the Zone Director")
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)        

    def _testCreateWlanOnZoneDirector(self):
        logging.info("Configure a WLAN with SSID %s and VLAN ID %s on the Zone Director" % (self.wlan_cfg['ssid'],
                                                                                            self.wlan_cfg['vlan_id']))
        self.errmsg = ""
        invalid_id_detected = False
        try:
            self.zd.cfg_wlan(self.wlan_cfg)

        except Exception, e:
            # Verify if the ZD allows to configure invalid VLAN IDs or not
            logging.debug("Catched exception %s" % e.message)
            invalid_id_msg = self.zd.messages['E_FailVLAN']
            invalid_id_msg = invalid_id_msg.replace("{1}", "VLAN")
            if invalid_id_msg in e.message:
                invalid_id_detected = True

            else:
                raise

        if not self.is_id_valid:
            if not invalid_id_detected:
                self.errmsg = "The Zone Director allowed to use the VLAN ID %s" % self.wlan_cfg['vlan_id']

    def _testStationAssocWithSSID(self):
        self.errmsg = tmethod.assoc_station_with_ssid(self.target_station, self.wlan_cfg, self.check_status_timeout)

    def _testRenewWifiIpAddress(self):
        (self.anOK, self.sta_wifi_ip_addr, self.sta_wifi_mac_addr) = \
        (self.anOK, self.xtype, self.errmsg) = tmethod.renew_wifi_ip_address(self.target_station, self.check_status_timeout)

        # we use self.errmsg to indicate method PASS or FAIL; so set to '' if everything is an OK
        if self.anOK:
            self.errmsg = ""
            return self.errmsg
        elif self.xtype == "FAIL":
            return self.errmsg
        else:
            raise Exception(self.errmsg)

    def _testIPAddressAssignment(self):
        logging.info("Make sure that the wireless station has got an IP address assigned to the VLAN")
        if utils.get_network_address(self.sta_wifi_ip_addr, self.mask) != utils.get_network_address(self.ip_addr, self.mask):
            self.errmsg = "The IP address %s was not in the same subnet as %s" % (self.sta_wifi_ip_addr, self.ip_addr)
        else:
            self.errmsg = ""

    def _testStationConnectivity(self):
        self.errmsg = tmethod.client_ping_dest_is_allowed(self.target_station, self.ip_addr, ping_timeout_ms = self.ping_timeout * 1000)

    def _testVerifyStationInfoOnZD(self):
        logging.info("Verify information of the target station shown on the Zone Director")
        exp_client_info = {"ip": self.sta_wifi_ip_addr, "status": "Authorized", "wlan": self.wlan_cfg['ssid']}

        self.errmsg, client_info = tmethod.verify_zd_client_status(self.zd, self.sta_wifi_mac_addr, exp_client_info,
                                                        self.check_status_timeout)

