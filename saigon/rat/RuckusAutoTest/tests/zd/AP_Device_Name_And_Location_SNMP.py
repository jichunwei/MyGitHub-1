# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: To verify AP Device configuration on Zone Director apply correct to AP or not

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
   - 'active_ap': the AP symbolic name
   - 'ap_device_cfg': A dictionary of AP Device configuration

   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - Prepare the active AP for testing
       - Save current AP Device Configuration

   2. Test:
       - Configure AP Device Configuration base on test parameters.
       - Log on to AP CLI and verify AP Device configuration applied correctly.
       - Using SNMP tool to get AP Device configuration and verify AP Device Configuration return correctly.

   3. Cleanup:
       - Restore AP Device Configuration
"""
import logging
import time

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import snmp_hlp as snmphlp
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8


class AP_Device_Name_And_Location_SNMP(Test):
    required_components = ['Zone Director', 'L3 Switch', 'Active AP']
    test_parameters = {'active_ap': 'the AP symbolic name',
                       'ap_device_cfg': 'A dictionary of AP Device Configuration',
                       'oid': 'SNMP OIDs to get AP Device Configuration'}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cfgActiveAP()
        self._cfgGetCurrentAPDeviceCfg()
        self._cfgSaveSNMPSettings()

    def test(self):
        self._cfgEnableSNMP()
        self._cfg_apDeviceCfgOnZD()

        self._testAPDeviceCfgUsingCLI()
        if self.errmsg: return ('FAIL', self.errmsg)

        self._testAPDeviceCfgUsingSNMP()
        if self.errmsg: return ('FAIL', self.errmsg)

        self.passmsg = "AP Device configuration work properly"
        return ('PASS', self.passmsg)

    def cleanup(self):
        self._restoreAPDeviceConfig()
        self._cfgRestoreSNMPSettings()

    # config
    def _initTestParameters(self, conf):

        self.conf = {'test_case':'',
                     'active_ap':'',
                     'check_status_timeout': 30
                     }

        self.conf.update(conf)

        if not self.conf.has_key('snmp_agent_cfg'):
            self.conf['snmp_agent_cfg'] = dict(enabled = True,
                                               contact = "support@ruckuswireless.com",
                                               location = "880 West Maude Avenue Suite 16",
                                               ro_community = "public",
                                               rw_community = "private")

        self.zd = self.testbed.components['ZoneDirector']
        self.current_snmp_agent_cfg = ""
        self.current_snmp_trap_cfg = ""
        self.active_ap = None

        self.errmsg = ''
        self.passmsg = ''

        self.current_ap_device_cfg = dict()

    def _cfgActiveAP(self):
        self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
        if not self.active_ap:
            raise Exception("Active AP (%s) not found in testbed" % self.conf['active_ap'])

    def _cfgGetCurrentAPDeviceCfg(self):
        logging.info("Get Current Active AP [%s] Device Cofiguration" % self.active_ap.base_mac_addr.upper())
        self.current_ap_device_cfg = lib.zd.ap.get_ap_device_info(self.zd, self.active_ap.base_mac_addr)

    def _cfgSaveSNMPSettings(self):
        # backup SNMP for restore in cleanup
        logging.info("Backup Current SNMP setting on Zone Director")
        self.current_snmp_agent_cfg = lib.zd.sys.get_snmp_agent_info(self.zd)
        self.current_snmp_trap_cfg = lib.zd.sys.get_snmp_trap_info(self.zd)

    def _cfgEnableSNMP(self):
        lib.zd.sys.set_snmp_agent_info(self.zd, self.conf['snmp_agent_cfg'])


    # test
    def _cfg_apDeviceCfgOnZD(self):
        logging.info("Set AP Device Configuration on ZD for AP[%s]" % self.active_ap.base_mac_addr)
        lib.zd.ap.set_ap_device_info(self.zd, self.active_ap.base_mac_addr, self.conf['ap_device_cfg'])
        logging.info("Wait for AP[%s] received updated configuration from Zone Director" % self.active_ap.base_mac_addr)
        time.sleep(self.conf['check_status_timeout'])

    def _testAPDeviceCfgUsingCLI(self):
        if self.conf['ap_device_cfg'].has_key('device_name'):
            logging.info("Test AP Device Name on AP CLI")
            ap_device_name = self.active_ap.get_device_name()
            logging.info("AP Device Name on AP CLI: %s" % ap_device_name)
            if ap_device_name != self.conf['ap_device_cfg']['device_name']:
                self.errmsg += "AP Device Name on AP CLI is different with AP Device Name configured on ZD"

        if self.conf['ap_device_cfg'].has_key('device_location'):
            logging.info("Test AP Device Location on AP CLI")
            ap_device_location = self.active_ap.get_device_location()
            if ap_device_location != self.conf['ap_device_cfg']['device_location']:
                self.errmsg += "AP Device Location on AP CLI is different with AP Device Location configured on ZD"

        if self.conf['ap_device_cfg'].has_key('gps_coordinates'):
            logging.info("Test AP Device GPS Coordinates on AP CLI")
            ap_device_gps = self.active_ap.get_device_gps()
            if ap_device_gps['latitude'] != self.conf['ap_device_cfg']['gps_coordinates']['latitude']:
                self.errmsg += "AP Device GPS Coordinate (latitude) on AP CLI is different with AP Device GPS \
                Coordinate (latitude) configured on ZD"

            if ap_device_gps['longitude'] != self.conf['ap_device_cfg']['gps_coordinates']['longitude']:
                self.errmsg += "AP Device GPS Coordinate (longitude) on AP CLI is different with AP Device GPS \
                Coordinate (longitude) configured on ZD"

    def _testAPDeviceCfgUsingSNMP(self):
        oid = [int(x) for x in self.conf['oid'].split('.')]
        oid.append(0)
        oid = tuple(oid)
        snmp_values = snmphlp.snmp_get(self.active_ap.ip_addr, self.conf['snmp_agent_cfg']['ro_community'], oid)
        if not snmp_values:
            self.errmsg += "received an empty string via SNMP"
            return

        if self.conf['ap_device_cfg'].has_key('device_name'):
            logging.info("Test AP Device Name using SNMP with OID = [%s]" % self.conf['oid'])
            found = False
            for snmp_value in snmp_values:
                if self.conf['ap_device_cfg']['device_name'] in snmp_value: found = True
            if not found:
                self.errmsg += "received incorrect AP Device Name via SNMP"

        if self.conf['ap_device_cfg'].has_key('device_location'):
            logging.info("Test AP Device Location using SNMP with OID = [%s]" % self.conf['oid'])
            found = False
            for snmp_value in snmp_values:
                if self.conf['ap_device_cfg']['device_location'] in snmp_value: found = True
            if not found:
                self.errmsg += "received incorrect AP Device Location via SNMP"

        if self.conf['ap_device_cfg'].has_key('gps_coordinates'):
            logging.info("Test AP Device GPS Coordinate using SNMP with OID = [%s]" % self.conf['oid'])
            found = False
            gps_value = "%s,%s" % (self.conf['ap_device_cfg']['gps_coordinates']['latitude'],
                                   self.conf['ap_device_cfg']['gps_coordinates']['longitude'])
            for snmp_value in snmp_values:
                logging.debug("snmp_value: %s, gps_value: %s" % (snmp_value, gps_value))
                if gps_value in snmp_value: found = True
            if not found:
                self.errmsg += "received incorrect AP Device Device GPS Coordinate via SNMP"

    # cleanup
    def _restoreAPDeviceConfig(self):
        logging.info("Restore Active AP [%s] Device Configuration" % self.active_ap.base_mac_addr.upper())

    def _cfgRestoreSNMPSettings(self):
        logging.info("Restore Current SNMP setting on Zone Director")
        if self.current_snmp_agent_cfg:
            lib.zd.sys.set_snmp_agent_info(self.zd, self.current_snmp_agent_cfg)
        if self.current_snmp_trap_cfg:
            lib.zd.sys.set_snmp_trap_info(self.zd, self.current_snmp_trap_cfg)
