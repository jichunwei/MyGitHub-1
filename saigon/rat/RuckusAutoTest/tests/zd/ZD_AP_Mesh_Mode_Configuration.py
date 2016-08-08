# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script use to test for the Mesh mode test suite which force the AP mesh mode to Auto/Root/Mesh/Disable
Author: An Nguyen
Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'testcase': the short name of test case. Ex: 'force-mesh-mode-to-auto'
                    'active_ap': the AP symbolic name

   Result type: PASS/FAIL/ERROR
   Results:

   Messages: If FAIL the test script return a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
        - Prepare the active AP for testing
   2. Test:
        - Base on the test case:
           + Force AP Mesh mode to the appropriate mode
           + Unplug AP out of system and verify AP reconnect to system in the correct mode with expected status
           + Plug AP in to system and verify AP reconnect to system in the correct mode with expected status
   3. Cleanup:
        - Clean up the testing environment by remove all non default configuration on ZD,
        target station, and active AP.


"""
import time
import logging

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class ZD_AP_Mesh_Mode_Configuration(Test):
    required_components = ['Zone Director', 'L3 Switch', 'Active AP']
    test_parameters = {'testcase': 'the short name of test case. Ex: "force-mesh-mode-to-auto"',
                       'active_ap': 'the AP symbolic name'}

    def config(self, conf):
        self._initTestParameters(conf)
        self._cfgActiveAP()

    def test(self):
        # Verify if Mesh is enabled on ZD, if not raise exception
        if not self.zd.get_mesh_cfg()['mesh_enable']:
            raise Exception('Mesh option is not enabled on Zone Director. The test will be broken')

        # Force AP Mesh mode base on the test parameters
        self._cfg_apMeshMode(self.mesh_mode_info['mode'])
        if self.errmsg:
            return ('FAIL', self.errmsg)

        # Unplugged AP out of system and verify
        self._cfgUnplugAPOutOfSystem()
        self._testAPConnectionStatus(self.mesh_mode_info['unplug_status'])
        if self.errmsg:
            return ('FAIL', '[AP cable is unplugged out of system] %s' % self.errmsg)

        self._testAPMeshMode(self.mesh_mode_info['mode'])
        if self.errmsg:
            return ('FAIL', '[AP cable is unplugged out of system] %s' % self.errmsg)

        # Plugged AP in to system and verify
        self._cfgPlugAPInToSystem()
        self._testAPConnectionStatus(self.mesh_mode_info['plug_status'])
        if self.errmsg:
            return ('FAIL', '[AP cable is plugged into system] %s' % self.errmsg)

        self._testAPMeshMode(self.mesh_mode_info['mode'])
        if self.errmsg:
            return ('FAIL', '[AP cable is plugged into system] %s' % self.errmsg)

        self.passmsg = 'AP [%s] is force to Mesh mode "%s" successfully'
        return ('PASS', self.passmsg % (self.active_ap.base_mac_addr, self.mesh_mode_info['mode']))

    def cleanup(self):
        if self.active_ap:
            self._cfg_apMeshMode('auto')
            self._cfgPlugAPInToSystem()
            self._testAPConnectionStatus('Root AP')
            if self.errmsg:
                raise Exception(self.errmsg)

    # Configuration
    def _initTestParameters(self, conf):
        self.conf = {'testcase':'',
                     'active_ap':'',
                     'check_status_timeout': 180}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.l3switch = self.testbed.components['L3Switch']
        self.active_ap = None

        self.errmsg = ''
        self.passmsg = ''

        self.mesh_mode_info = {'force-mesh-mode-to-auto': {'mode': 'auto',
                                                           'unplug_status':'Mesh AP',
                                                           'plug_status':'Root AP'},
                               'force-mesh-mode-to-root': {'mode': 'root',
                                                           'unplug_status':'Disconnected',
                                                           'plug_status':'Root AP'},
                               'force-mesh-mode-to-mesh': {'mode': 'mesh',
                                                           'unplug_status':'Mesh AP',
                                                           'plug_status':'Mesh AP'},
                               'force-mesh-mode-to-disabled': {'mode': 'disabled',
                                                               'unplug_status':'Disconnected',
                                                               'plug_status':'Connected'}
                               }[self.conf['testcase']]

    def _cfgActiveAP(self):
        self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
        if not self.active_ap:
            raise Exception("Active AP (%s) not found in testbed" % self.conf['active_ap'])
        self.active_ap.base_mac_addr.lower()
        self.active_ap_connection_port = self.testbed.mac_to_port[self.active_ap.base_mac_addr.lower()]

    def _cfg_apMeshMode(self, mode):
        current_mesh_mode = lib.zd.ap.get_cfg_info_by_mac_addr(self.zd, self.active_ap.base_mac_addr)['mesh_mode']
        if current_mesh_mode.lower() != mode.lower():
            lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, {'mesh_mode': mode.lower()})

            self._verifyIsAPReboot()
            if self.errmsg:
                logging.info(self.errmsg)
                return

            self._testAPConnectionStatus()
            if self.errmsg:
                logging.info(self.errmsg)
                return

    def _cfgUnplugAPOutOfSystem(self):
        logging.info("Close connection to AP [%s %s] before disabling its switch port."
                    % (self.active_ap.base_mac_addr, self.active_ap.ip_addr))
        self.active_ap.close()
        logging.info("Disable the switch port %s connected to the AP [%s %s]" \
                    % (self.active_ap_connection_port,
                       self.active_ap.base_mac_addr, self.active_ap.ip_addr))
        self.l3switch.disable_interface(self.active_ap_connection_port)
        time.sleep(10)

    def _cfgPlugAPInToSystem(self):
        logging.info("Enable the switch port %s connected to the AP [%s]" \
                    % (self.active_ap_connection_port,
                       self.active_ap.base_mac_addr))
        self.l3switch.enable_interface(self.active_ap_connection_port)


    def _verifyIsAPReboot(self, reboot_timeout = 60):
        start_time = time.time()
        time_out = time.time() - start_time
        rebooted = True

        while time_out < reboot_timeout:
            time_out = time.time() - start_time
            try:
                current_uptime = self.active_ap.get_up_time()
                if current_uptime['days'] is None and current_uptime['hrs'] is None :
                    run_time = 0
                    if current_uptime['mins']:
                        run_time = int(current_uptime['mins']) * 60
                    run_time = run_time + int(current_uptime['secs'])
                    if run_time < reboot_timeout + 15 :
                        rebooted = True
                        break
                else :
                    rebooted = False
                time.sleep( 3 )

            except Exception, e:
                rebooted = True
                # logging.info('exception info: %s' % e.message)
                if e.message.__contains__('haven\'t matched the uptime info'):
                    raise e
                logging.info('Active AP is rebooting')
                time.sleep(10)
                break

        if not rebooted:
            msg = 'AP [%s] does not reboot after %s seconds'
            self.errmsg = msg % (self.active_ap.base_mac_addr, repr(reboot_timeout))


    def _testAPConnectionStatus(self, expected_status = 'Connected'):
        # Wait until AP reboot successfully
        start_time = time.time()
        time_out = time.time() - start_time
        flag = False

        while time_out < self.conf['check_status_timeout']:
            time_out = time.time() - start_time
            ap_info = self.zd.get_all_ap_info(self.active_ap.base_mac_addr)
            if expected_status in ap_info['status']:
                if expected_status != 'Disconnected':
                    self.active_ap.verify_component()
                flag = True
                break

        if not flag:
            msg = 'AP [%s] is still %s instead of %s after %s'
            self.errmsg = msg % (self.active_ap.base_mac_addr, ap_info['status'], expected_status,
                                 self.conf['check_status_timeout'])

    def _testAPMeshMode(self, expected_mesh_mode):
        ap_info = self.zd.get_all_ap_info(self.active_ap.base_mac_addr)

        if ap_info['mesh_mode'].lower() != expected_mesh_mode.lower():
            self.errmsg = 'The AP Mesh mode is "%s" instead of %s' % (ap_info['mesh_mode'], expected_mesh_mode)
            return

        msg = '[Corrected Info] AP status is "%s" with Mesh mode is "%s"'
        logging.info(msg % (ap_info['status'], ap_info['mesh_mode']))
