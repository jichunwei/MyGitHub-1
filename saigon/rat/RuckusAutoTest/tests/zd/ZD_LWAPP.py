# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: Verify the ability of the AP to discover the ZD by using different methods

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'active_ap': 'Symbolic name or MAC address of the active AP',
                    'conn_mode': 'Connection mode of the AP will be verified',
                    'discovery_method': 'ZD discovery method: fixed-pri, fixed-sec, dhcp, dns, record, or ""',
                    'pre_conn_mode': 'Connection mode of the AP before running the test',
                    'pre_discovery_method': ' ZD discovery mothod used before running the test'

   Result type: PASS/FAIL/ERROR
   Results: PASS: if the AP could discover the ZD successfully using the given discovery method
            FAIL: if one of the above criteria is not satisfied
            ERROR: if some unexpected events happen

   Test procedure:
   1. Config:
   2. Test:
           - Configure DHCP server to provide option 15 or 43 depending on the tests
           - Configure the AP and the Netgear switch to make the AP become an L2 or L3 AP depending on the tests
           - Verify AP connection and other information shown on AP's Linux shell
           - Repeat the above two steps if a new connection mode is required
   3. Cleanup:
           - Restart DHCP server to original configuration will all the options enabled.
"""

import os
import re
import logging
import time

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils

class ZD_LWAPP(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {'active_ap': 'Symbolic name or MAC address of the active AP',
                           'conn_mode': 'Connection mode of the AP will be verified',
                           'discovery_method': 'ZD discovery method: fixed_pri, fixed_sec, dhcp, dns, record, or ""',
                           'pre_conn_mode': 'Connection mode of the AP before running the test',
                           'pre_discovery_method': ' ZD discovery mothod used before running the test'}

    def config(self, conf):
        # Prepare test parameters
        self._cfgInitTestParams(conf)

        # In some tests that the AP needs to be reset factory, the ZD running mesh will force the AP to reboot twice
        # That causes the "Found ZD through" message become "last joined ZD"
        # So, it is necessary to disable mesh to verify the test cases
        self._cfgDisableMeshOnZD()

    def test(self):
        self._cfgDhcpOptions(before_test = True)

        self._cfgActiveAP(before_test = True)

        self._testActiveAP(before_test = True)
        if self.err_msg: return ("FAIL", self.err_msg)

        self._cfgDhcpOptions(before_test = False)

        self._cfgActiveAP(before_test = False)

        self._testActiveAP(before_test = False)
        if self.err_msg: return ("FAIL", self.err_msg)

        return ("PASS", "")

    def cleanup(self):
        if (self.conf.has_key("pre_discovery_method") and self.conf["pre_discovery_method"] in ["dns", "dhcp"]) or \
           (self.conf.has_key("discovery_method") and self.conf["discovery_method"] in ["dns", "dhcp"]):
            logging.info("Enable DHCP option 15 on the Linux server")
            self.testbed.components["LinuxServer"].set_dhcp_option_15(True)
            logging.info("Enable DHCP option 43 on the Linux server")
            ip_list = [self.testbed.components["ZoneDirector"].ip_addr]
            self.testbed.components["LinuxServer"].set_dhcp_option_43(True, ip_list)
            
        #@author: anzuo, @change: change SW port vlan to default 301
        if self.testbed.mac_to_vlan[self.active_ap_mac] != '301':
            ap_obj = self.testbed.mac_to_ap[self.active_ap_mac]
            ap_obj.reboot(login=False)
            logging.info("change AP SW port config back to 301")
            sw = self.testbed.components["L3Switch"]
            sw.remove_interface_from_vlan(self.testbed.mac_to_port[self.active_ap_mac],self.testbed.mac_to_vlan[self.active_ap_mac])
            sw.add_interface_to_vlan(self.testbed.mac_to_port[self.active_ap_mac],'301')
            logging.info("wait 60 seconds")
            time.sleep(60)
        
        self.testbed.components["ZoneDirector"].wait_aps_join_in_zd()
        
        logging.info("Detect the new IP leased of the AP at new VLAN")
        self.testbed._detect_ap_dynamic_addresses([self.active_ap_mac])
        logging.debug("MAC to IP table: %s" % self.testbed.mac_to_ip)
        ap_obj.ip_addr = self.testbed.mac_to_ip[self.active_ap_mac]
            

    def _cfgInitTestParams(self, conf):
        self.conf = conf
        self.active_ap = None
        self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
        if not self.active_ap:
            raise Exception("Active AP (%s) not found in test bed" % self.conf['active_ap'])
        self.active_ap_mac = self.active_ap.get_base_mac().lower()
        self.err_msg = ""

    def _cfgDisableMeshOnZD(self):
        mesh_conf = self.testbed.components['ZoneDirector'].get_mesh_cfg()
        if not mesh_conf['mesh_enable']:
            logging.info("Mesh has been disabled")
            return
        self.testbed.disable_mesh()

    def _cfgDhcpOptions(self, before_test):
        method = ""
        if before_test:
            if self.conf.has_key("pre_conn_mode") and self.conf.has_key("pre_discovery_method"):
                method = self.conf["pre_discovery_method"]
        else:
            if self.conf.has_key("conn_mode") and self.conf.has_key("discovery_method"):
                method = self.conf["discovery_method"]
        if method and method == "dns":
            logging.info("Enable DHCP option 15 on the Linux server")
            self.testbed.components["LinuxServer"].set_dhcp_option_15(True)
            logging.info("Disable DHCP option 43 on the Linux server")
            self.testbed.components["LinuxServer"].set_dhcp_option_43(False)
        elif method and method == "dhcp":
            logging.info("Enable DHCP option 43 on the Linux server")
            ip_list = [self.testbed.components["ZoneDirector"].ip_addr]
            self.testbed.components["LinuxServer"].set_dhcp_option_43(True, ip_list)
            logging.info("Disable DHCP option 15 on the Linux server")
            self.testbed.components["LinuxServer"].set_dhcp_option_15(False)

    def _cfgActiveAP(self, before_test):
        if before_test:
            if self.conf.has_key("pre_conn_mode") and self.conf.has_key("pre_discovery_method"):
                logging.info("Configure the AP '%s' to LWAPP mode '%s' using method '%s' - before running test" % \
                             (self.active_ap_mac, self.conf["pre_conn_mode"], self.conf["pre_discovery_method"]))
                self.testbed.configure_ap_connection_mode(self.active_ap_mac, self.conf["pre_conn_mode"],
                                                       self.conf["pre_discovery_method"])
        else:
            if self.conf.has_key("conn_mode") and self.conf.has_key("discovery_method"):
                logging.info("Configure the AP '%s' to LWAPP mode '%s' using method '%s'" % \
                             (self.active_ap_mac, self.conf["conn_mode"], self.conf["discovery_method"]))
                self.testbed.configure_ap_connection_mode(self.active_ap_mac, self.conf["conn_mode"],
                                                       self.conf["discovery_method"])

    def _testActiveAP(self, before_test):
        if before_test:
            if self.conf.has_key("pre_conn_mode") and self.conf.has_key("pre_discovery_method"):
                logging.info("Verify the connection mode of AP '%s' - before running test" % self.active_ap_mac)
                self.err_msg = self.testbed.verify_ap_connection_mode(self.active_ap_mac, self.conf["pre_discovery_method"])
        else:
            if self.conf.has_key("conn_mode") and self.conf.has_key("discovery_method"):
                logging.info("Verify the connection mode of AP '%s'" % self.active_ap_mac)
                self.err_msg = self.testbed.verify_ap_connection_mode(self.active_ap_mac, self.conf["discovery_method"])

