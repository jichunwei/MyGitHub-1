# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.

"""
Description: This script use to test for the Mesh mode test suite which force the AP mesh mode to Auto/Root/Mesh/Disable
Author: An Nguyen
Email: an.nguyen@ruckuswireless.com

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'test_option': the short name of test case. Ex: 'force-mesh-mode-to-auto'
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

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_AP_Mesh_Mode_Configuration(Test):
    required_components = ['Zone Director', 'L3 Switch', 'Active AP']
    test_parameters = {'test_option': 'the short name of test case. Ex: "force-mesh-mode-to-auto"',
                       'active_ap': 'the AP symbolic name'}

    def config(self, conf):
        self._init_test_parameters(conf)
        self._cfg_active_ap()

    def test(self):
        # Verify if Mesh is enabled on ZD, if not raise exception
        if not self.zd.get_mesh_cfg()['mesh_enable']:
            raise Exception('Mesh option is not enabled on Zone Director. The test will be broken')

        # Force AP Mesh mode base on the test parameters
        self._cfg_ap_mesh_mode(self.mesh_mode_info['mode'])
        if self.errmsg:
            return ('FAIL', self.errmsg)

        # Unplugged AP out of system and verify
        self._cfg_unplug_ap_out_of_system()
        self._test_ap_connection_status(self.mesh_mode_info['unplug_status'])
        if self.errmsg:
            return ('FAIL', '[AP cable is unplugged out of system] %s' % self.errmsg)

        self._test_ap_mesh_mode(self.mesh_mode_info['mode'])
        if self.errmsg:
            return ('FAIL', '[AP cable is unplugged out of system] %s' % self.errmsg)

        # Plugged AP in to system and verify
        self._cfg_plug_ap_in_to_system()
        self._test_ap_connection_status(self.mesh_mode_info['plug_status'])
        if self.errmsg:
            return ('FAIL', '[AP cable is plugged into system] %s' % self.errmsg)

        self._test_ap_mesh_mode(self.mesh_mode_info['mode'])
        if self.errmsg:
            return ('FAIL', '[AP cable is plugged into system] %s' % self.errmsg)

        self.passmsg = 'AP [%s] is force to Mesh mode "%s" successfully'
        return ('PASS', self.passmsg % (self.active_ap.base_mac_addr, self.mesh_mode_info['mode']))

    def cleanup(self):
        if self.active_ap:
            self._cfg_ap_mesh_mode('auto')
            self._cfg_plug_ap_in_to_system()
            self._test_ap_connection_status('Root AP')
            if self.errmsg:
                raise Exception(self.errmsg)

    # Configuration
    def _init_test_parameters(self, conf):
        self.conf = {'test_option':'',
                     'ap_tag':'',
                     'check_status_timeout': 240}
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
                               }[self.conf['test_option']]

    def _cfg_active_ap(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.active_ap_connection_port = self.testbed.mac_to_port[self.active_ap.base_mac_addr]

    def _cfg_ap_mesh_mode(self, mode):
        current_mesh_mode = lib.zd.ap.get_cfg_info_by_mac_addr(self.zd, self.active_ap.base_mac_addr)['mesh_mode']
        if current_mesh_mode.lower() != mode.lower():
            lib.zd.ap.cfg_ap(self.zd, self.active_ap.base_mac_addr, {'mesh_mode': mode.lower()})

            self._verify_is_ap_reboot()
            if self.errmsg:
                logging.info(self.errmsg)
                return

            self._test_ap_connection_status()
            if self.errmsg:
                logging.info(self.errmsg)
                return

    def _cfg_unplug_ap_out_of_system(self):
        logging.info("Close connection to AP [%s %s] before disabling its switch port."
                    % (self.active_ap.base_mac_addr, self.active_ap.ip_addr))
        self.active_ap.close()
        logging.info("Disable the switch port %s connected to the AP [%s %s]" \
                    % (self.active_ap_connection_port,
                       self.active_ap.base_mac_addr, self.active_ap.ip_addr))
        self.l3switch.disable_interface(self.active_ap_connection_port)
        time.sleep(10)

    def _cfg_plug_ap_in_to_system(self):
        logging.info("Enable the switch port %s connected to the AP [%s]" \
                    % (self.active_ap_connection_port,
                       self.active_ap.base_mac_addr))
        self.l3switch.enable_interface(self.active_ap_connection_port)


    def _verify_is_ap_reboot(self, reboot_timeout = 60):
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


    def _test_ap_connection_status(self, expected_status = 'Connected'):
        # Wait until AP reboot successfully
        start_time = time.time()
        time_out = time.time() - start_time
        flag = False

        while time_out < self.conf['check_status_timeout']:
            time_out = time.time() - start_time
            ap_info = self.zd.get_all_ap_info(self.active_ap.base_mac_addr)
            if expected_status in ap_info['status']:
                if expected_status != 'Disconnected':
                    try:
                        self.active_ap.verify_component()
                    except:
                        time.sleep(30)
                        self.active_ap.verify_component()                        
                flag = True
                break
            time.sleep(30)

        if not flag:
            msg = 'AP [%s] is still %s instead of %s after %s'
            self.errmsg = msg % (self.active_ap.base_mac_addr, ap_info['status'], expected_status,
                                 self.conf['check_status_timeout'])

    def _test_ap_mesh_mode(self, expected_mesh_mode):
        ap_info = self.zd.get_all_ap_info(self.active_ap.base_mac_addr)

        if ap_info['mesh_mode'].lower() != expected_mesh_mode.lower():
            self.errmsg = 'The AP Mesh mode is "%s" instead of %s' % (ap_info['mesh_mode'], expected_mesh_mode)
            return

        msg = '[Corrected Info] AP status is "%s" with Mesh mode is "%s"'
        logging.info(msg % (ap_info['status'], ap_info['mesh_mode']))