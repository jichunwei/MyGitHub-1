# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)

"""

import os
import re
import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components import NetgearSwitchRouter
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8


# Note that the name of the Test class must match the name of this file for ease of runtime-reference

class CB_ZD_Wired_Mesh_Network_Test(Test):
    required_components = []
    parameter_description = {}

    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        self.test_function[self.conf['testcase']]()
        if self.errmsg: return ('FAIL', self.errmsg)
        passmsg = self.passmsg

        return ('PASS', passmsg)

    def cleanup(self):
        pass

    def _initTestParameters(self, conf):
        self.conf = {'wired_mesh_network_forming_cmd_set': """
                                                           interface %s
                                                           vlan participation exclude 2
                                                           no vlan tagging 2
                                                           vlan participation exclude 302
                                                           no vlan tagging 302
                                                           vlan participation exclude 3677
                                                           no vlan tagging 3677
                                                           vlan participation exclude 301
                                                           vlan participation include 777
                                                           vlan pvid 777
                                                           vlan participation include 110
                                                           vlan tagging 110
                                                           """,
                    'become_root_cmd_set': """
                                           interface %s
                                           vlan participation include 301
                                           vlan pvid 301
                                           vlan participation include 2
                                           vlan tagging 2
                                           vlan participation include 302
                                           vlan tagging 302
                                           vlan participation include 3677
                                           vlan tagging 3677
                                           vlan participation exclude 110
                                           no vlan tagging 110
                                           vlan participation exclude 777
                                           """,
                    'mesh_link_aps_list': [],
                    'waiting_time': 2000,
                    'check_status_timeout': 180,
                    }
        self.conf.update(conf)

        self.zd = self.testbed.components['ZoneDirector']
        self.l3switch = NetgearSwitchRouter.NetgearSwitchRouter(self.testbed.components['L3Switch'].conf)

        if self.carrierbag.get('existing_aps_connection_status'):
            self.existing_aps_connection_status = self.carrierbag['existing_aps_connection_status']
        else:
            self.existing_aps_connection_status = lib.zd.ap.get_all_ap_info(self.zd)

        self._getAPsInfoBySymName()
        self.mesh_link_aps_port_list = [ap_info['port'] for ap_info in self.mesh_link_aps_info.values()]
        self.mesh_link_aps_mac_list = [ap_info['mac'] for ap_info in self.mesh_link_aps_info.values()]

        print self.mesh_link_aps_mac_list, self.mesh_link_aps_port_list

        self.test_function = {'form_wired_mesh_network': self._testFormWiredMeshNetwork,
                              'mesh_ap_temporary_out_of_service': self._testMeshAPTemporaryOutOfService,
                              'link_ap_temporary_out_of_service': self._testLinkAPTemporaryOutOfService,
                              'mesh_ap_become_root': self._testMeshAPBecomesRootAP,
                              'link_ap_become_root': self._testLinkAPBecomesRootAP,
                              'zd_temporary_out_of_service': self._testZoneDirectorTemporaryOutOfService,
                              'all_aps_become_root': self._testAllAPsBecomeRootAPs,
                              }

        self.errmsg = ''
        self.passmsg = ''

    def _getMeshAP(self):
        # Return the object of the first Mesh AP in system
        logging.info('Pick up a Mesh AP to test')
        current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        for ap in current_aps_info.values():
            if ap['status'] == 'Connected (Mesh AP, 1 hop)':
                return tconfig.get_active_ap(ap['mac_address'], self.testbed.components['AP'], 'Mesh AP')
        raise Exception('[Test broken] There is not any Mesh AP in system')

    def _getLinkAP(self):
        # Return the object of the first Link AP in system
        logging.info('Pick up a Link AP to test')
        current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        for ap in current_aps_info.values():
            if ap['status'] == 'Connected (Link AP, 2 hops)':
                return tconfig.get_active_ap(ap['mac_address'], self.testbed.components['AP'], 'Link AP')
        raise Exception('[Test broken] There is not any Link AP in system')

    def _reboot_ap(self, ap):
        logging.info('Reboot AP[%s, %s]' % (ap.base_mac_addr, ap.ip_addr))
        lib.zd.ap.reboot_ap(self.zd, ap.base_mac_addr.lower())

    def _rebootZD(self):
        logging.info('Reboot Zone Director')
        lib.zd.admin.reboot_zd(self.zd)

    def _cfgVLANOnAPsPortToBecomeRoot(self, ap_port_list):
        logging.debug('Setting VLAN on ports %s' % ap_port_list)
        for ap_port in ap_port_list:
            self.l3switch.do_cfg(self.conf['become_root_cmd_set'] % ap_port)

    def _cfgVLANOnMeshAPPortToBecomeRoot(self):
        # Return the object of the first Mesh AP in system
        current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        for ap in current_aps_info.values():
            if ap['status'] == 'Connected (Mesh AP, 1 hop)':
                ap_port = self.testbed.mac_to_port[ap['mac_address']]
                logging.debug('Setting VLAN on connection port of the AP %s' % ap)
                self._cfgVLANOnAPsPortToBecomeRoot([ap_port])
                return ap['mac_address']
        raise Exception('[Test broken] There is not any Mesh AP in system')

    def _cfgVLANOnLinkAPPortToBecomeRoot(self):
        # Return the object of the first Mesh AP in system
        current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        for ap in current_aps_info.values():
            if ap['status'] == 'Connected (Link AP, 2 hops)':
                ap_port = self.testbed.mac_to_port[ap['mac_address']]
                logging.debug('Setting VLAN on connection port of the AP %s' % ap)
                self._cfgVLANOnAPsPortToBecomeRoot([ap_port])
                return ap['mac_address']
        raise Exception('[Test broken] There is not any Link AP in system')

    def _getAPsInfoBySymName(self):
        # Return the dictionary information of APs with keys are the symbolic names
        self.mesh_link_aps_info = {}
        for ap_name in self.conf['mesh_link_aps_list']:
            self.mesh_link_aps_info[ap_name] = {}
            ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(ap_name)
            self.mesh_link_aps_info[ap_name]['mac'] = ap_mac
            self.mesh_link_aps_info[ap_name]['port'] = self.testbed.mac_to_port[ap_mac]

    def _cfgVLANOnAPsPortToFormWiredMeshNetwork(self, ap_port_list):
        # Try to configure the VLAN setting on the Mesh/Link AP port
        logging.debug('Setting VLAN on ports %s' % ap_port_list)
        for ap_port in ap_port_list:
            self.l3switch.do_cfg(self.conf['wired_mesh_network_forming_cmd_set'] % ap_port)

    def _detectAPsRole(self, expected_ap_role_info):
        # Verify if the APs role is as expected
        all_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        root_aps = [ap for ap in all_aps_info.values() if ap['status'] == 'Connected (Root AP)']
        mesh_aps = [ap for ap in all_aps_info.values() if ap['status'] == 'Connected (Mesh AP, 1 hop)']
        link_aps = [ap for ap in all_aps_info.values() if ap['status'] == 'Connected (Link AP, 2 hops)']

        current_ap_role_info = {'root_ap': len(root_aps),
                                'mesh_ap': len(mesh_aps),
                                'link_ap': len(link_aps)}

        logging.debug('[Current APs role structure]: %s' % current_ap_role_info)
        if current_ap_role_info != expected_ap_role_info:
            return False

        all_aps_connection_status = {}
        for ap in all_aps_info.keys():
            all_aps_connection_status[ap] = all_aps_info[ap]['status']

        self.carrierbag['existing_aps_connection_status'] = all_aps_connection_status
        return True

    def _verifyAPIsRoot(self, ap_mac, pause = 30):
        ap_info = lib.zd.ap.get_ap_info_by_mac(self.zd, ap_mac)
        if ap_info['status'] != 'Connected (Root AP)':
            msg = 'The status of AP[%s] is %s instead of Root AP'
            self.errmsg = msg % (ap_mac, ap_info['status'])
            logging.debug(self.errmsg)
            return
        self.passmsg = 'The AP[%s] is Root AP as expected' % ap_mac

    def _verifyTheWiredMeshNetworkForming(self):
        # Verify if the Wire Mesh Network is formed correctly
        logging.info('Verify the forming process')
        start_time = time.time()
        current_role = {'mesh_ap':0, 'link_ap':0}

        while True:
            run_time = time.time() - start_time
            if self._detectAPsRole(self.conf['expected_aps_role']):
                pass_time = 1
                check_time = 1
                while check_time < 3:
                    check_time += 1
                    if self._detectAPsRole(self.conf['expected_aps_role']):
                        pass_time += 1
                    else: break

                if pass_time == 3:
                    break

            if run_time > self.conf['waiting_time']:
                self.errmsg = 'The Wired Mesh Network is not formed correctly'
                return

        self.passmsg = 'The Wired Mesh Network is formed correctly with expected role %s' % self.conf['expected_aps_role']

    def _testFormWiredMeshNetwork(self):
        self._cfgVLANOnAPsPortToFormWiredMeshNetwork(self.mesh_link_aps_port_list)

        self._verifyTheWiredMeshNetworkForming()

    def _testMeshAPTemporaryOutOfService(self):
        # Reboot Mesh AP
        mesh_ap = self._getMeshAP()
        self._reboot_ap(mesh_ap)
        time.sleep(30)

        self._verifyTheWiredMeshNetworkForming()

    def _testLinkAPTemporaryOutOfService(self):
        # Reboot Link AP
        link_ap = self._getLinkAP()
        self._reboot_ap(link_ap)
        time.sleep(30)

        self._verifyTheWiredMeshNetworkForming()

    def _testMeshAPBecomesRootAP(self):
        mesh_become_root_ap_mac = self._cfgVLANOnMeshAPPortToBecomeRoot()
        remain_mesh_link_aps_list = list(set(self.mesh_link_aps_mac_list) - set([mesh_become_root_ap_mac]))

        self._verifyTheWiredMeshNetworkForming()
        if self.errmsg: return
        passmsg = self.passmsg

        self._verifyAPIsRoot(mesh_become_root_ap_mac)
        if self.errmsg: return
        self.passmsg = passmsg + ', ' + self.passmsg

        self.carrierbag['mesh_become_root_ap_mac'] = mesh_become_root_ap_mac

    def _testLinkAPBecomesRootAP(self):
        link_become_root_ap_mac = self._cfgVLANOnLinkAPPortToBecomeRoot()
        remain_mesh_link_aps_list = list(set(self.mesh_link_aps_mac_list) - set([link_become_root_ap_mac]))

        self._verifyTheWiredMeshNetworkForming()
        if self.errmsg: return
        passmsg = self.passmsg

        self._verifyAPIsRoot(link_become_root_ap_mac)
        if self.errmsg: return
        self.passmsg = passmsg + ', ' + self.passmsg

        self.carrierbag['link_become_root_ap_mac'] = link_become_root_ap_mac

    def _testZoneDirectorTemporaryOutOfService(self):
        self._rebootZD()

        become_root_aps_mac_list = [self.carrierbag['mesh_become_root_ap_mac'], self.carrierbag['link_become_root_ap_mac']]
        aps_port = [self.testbed.mac_to_port[ap] for ap in become_root_aps_mac_list]
        self._cfgVLANOnAPsPortToFormWiredMeshNetwork(aps_port)

        self._verifyTheWiredMeshNetworkForming()

    def _testAllAPsBecomeRootAPs(self):
        self._cfgVLANOnAPsPortToBecomeRoot(self.mesh_link_aps_port_list)

        self._verifyTheWiredMeshNetworkForming()

