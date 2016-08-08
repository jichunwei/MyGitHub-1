"""
Description: CB_ZD_MeshTree

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
    - 'meshtree_cfg': A dictionary of symbolic name AP that define structure of Mesh Tree base on uplink AP & downlink AP
    - 'test_case': A name of specific test for Mesh Tree refer to self.tc2f in config functions
   Result type: PASS/FAIL
   Results: PASS: if mesh tree forming correctly as original meshtree_cfg defined in carrierbag or in test params
            FAIL: if current mesh tree on Zone Director is different with meshtree_cfg

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
from copy import deepcopy
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_MeshTree(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                          }

    def config(self, conf):
        self.tc2f = {
            'create_meshtree': self._testCreateMeshTree,
            'verify_meshtree': self._testMeshTree,
            'verify_meshtree_change_channel': self._testChangeAPChannel,
            'verify_meshtree_reboot_ap': self._testRebootAP,
            'verify_meshtree_reboot_zonedirector': self._testRebootZD
        }
        self._cfgInitTestParams(conf)

    def test(self):
        self.tc2f[self.conf["test_case"]]()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        return self.returnResult("PASS", self.passmsg)

    def cleanup(self):
        pass
#
# Config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(check_status_timeout = 360,
                         check_wlan_timeout = 45,
                         pause = 2.0,
                         target_ap = None)

        self.conf.update(conf)
        self.errmsg = ""
        self.passmsg = ""
        self.zd = self.testbed.components['ZoneDirector']
        self.meshtree_cfg = dict()
        self.target_ap = self.conf['target_ap']
        if self.conf.has_key('meshtree_cfg'):
            self.carrierbag['meshtree_cfg'] = deepcopy(self.conf['meshtree_cfg'])
        else:
            self.conf.update(self.carrierbag)

    def _cfgConvertMeshTreeSymDictToMac(self):
        for ap in sorted(self.conf['meshtree_cfg'].keys()):
            self.meshtree_cfg[self.testbed.get_ap_mac_addr_by_sym_name(ap)] = dict()
            if self.conf['meshtree_cfg'][ap]['uplink_ap']:
                uplink_ap = self.conf['meshtree_cfg'][ap]['uplink_ap']
                self.meshtree_cfg[self.testbed.get_ap_mac_addr_by_sym_name(ap)]['uplink_ap'] = self.testbed.get_ap_mac_addr_by_sym_name(uplink_ap)
            else:
                self.meshtree_cfg[self.testbed.get_ap_mac_addr_by_sym_name(ap)]['uplink_ap'] = ""

            if self.conf['meshtree_cfg'][ap]['downlink_ap']:
                downlink_ap_list = []
                for downlink_ap in self.conf['meshtree_cfg'][ap]['downlink_ap']:
                    downlink_ap_list.append(self.testbed.get_ap_mac_addr_by_sym_name(downlink_ap))
                self.meshtree_cfg[self.testbed.get_ap_mac_addr_by_sym_name(ap)]['downlink_ap'] = downlink_ap_list
            else:
                self.meshtree_cfg[self.testbed.get_ap_mac_addr_by_sym_name(ap)]['downlink_ap'] = []

#
# test()
#
    def _testCreateMeshTree(self):
        logging.info("Create a Mesh Tree with configuration:\n%s" % pformat(self.conf['meshtree_cfg'], indent = 4))
        try:
            for ap in sorted(self.conf['meshtree_cfg'].keys()):
                if self.conf['meshtree_cfg'][ap]['uplink_ap']:
                    uplink_ap = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['meshtree_cfg'][ap]['uplink_ap'])
                    logging.info("Form mesh for AP[%s] with Uplink [%s]" % (ap, uplink_ap))
                    self.testbed.form_mesh([self.testbed.get_ap_mac_addr_by_sym_name(ap)], [(self.testbed.get_ap_mac_addr_by_sym_name(ap), [uplink_ap])])
            tmethod8.pause_test_for(self.conf['check_status_timeout'], "AP join Zone Director and form Mesh Tree")
        except Exception, msg:
            logging.debug(msg)
            self.errmsg = "Can't create mesh tree as design"
        self.passmsg = "Mesh tree created successful"

    def _testMeshTree(self):
        # meshtree configure exist etheir from test_param or from carrierbag
        self.conf.update(self.carrierbag)
        if not self.conf.has_key("meshtree_cfg"):
            self.errmsg = "Test case require Mesh Tree Config to verify Mesh Tree on Zone Director"
            logging.debug(self.errmsg)
            return

        # Convert current Mesh Tree from SymName to Mac Address
        self._cfgConvertMeshTreeSymDictToMac()

        logging.info("Verify current mesh tree status on Zone Director")
        aps_info_list = self.zd.get_all_ap_info()
        mesh_zd_adaptertree_cfg = dict()
        for ap in aps_info_list:
            ap_detail_cfg = lib.zd.aps.get_ap_detail_mesh_tree_by_mac_addr(self.zd, ap['mac'])

            mesh_zd_adaptertree_cfg[ap['mac']] = dict()
            mesh_zd_adaptertree_cfg[ap['mac']]['uplink_ap'] = ap_detail_cfg['uplink']['ap']
            mesh_zd_adaptertree_cfg[ap['mac']]['downlink_ap'] = []
            for downlink_ap in ap_detail_cfg['downlink'].iterkeys():
                mesh_zd_adaptertree_cfg[ap['mac']]['downlink_ap'].append(downlink_ap)

        logging.info("Current Mesh Tree on Zone Director: \n %s" % pformat(mesh_zd_adaptertree_cfg, indent = 4))
        if mesh_zd_adaptertree_cfg != self.meshtree_cfg:
            self.errmsg = "Current mesh tree configuration on Zone Director is different with Mesh Tree installed"
        else:
            self.passmsg += "Mesh tree configuration on Zone Director matches with Mesh Tree installed"

    def _testChangeAPChannel(self):
        logging.info("Get current channel of AP [%s]" % self.testbed.get_ap_mac_addr_by_sym_name(self.target_ap))
        active_ap_info = lib.zd.aps.get_ap_detail_radio_by_mac_addr(self.zd, self.testbed.get_ap_mac_addr_by_sym_name(self.target_ap))

        current_channel = active_ap_info['channel']
        logging.info("Channel channel of AP[%s] from channel %s to %s" % (self.testbed.get_ap_mac_addr_by_sym_name(self.target_ap),
                                                                          current_channel, self.conf['channel']))
        self.zd.set_ap_cfg({'mac_addr': self.testbed.get_ap_mac_addr_by_sym_name(self.target_ap),
                                    'channel': self.conf['channel']})

        tmethod8.pause_test_for(self.conf['check_status_timeout'], "Wait for Zone Director update channel to AP")
        logging.info("Verify Mesh Tree status after change AP channel")
        self._testMeshTree()
        if self.passmsg: self.passmsg = "Mesh Tree reformed correct after change channel to %s" % self.conf['channel']

    def _testRebootAP(self):
        logging.info("Reboot AP[%s] and verify Mesh Tree will not change after AP reboot" % self.testbed.get_ap_mac_addr_by_sym_name(self.target_ap))
        lib.zd.mma.restart_ap_by_mac(self.zd, self.testbed.get_ap_mac_addr_by_sym_name(self.target_ap))
        tmethod8.pause_test_for(self.conf['check_status_timeout'], "Wait for the AP rejoin Zone Director")

        logging.info("Verify Mesh Tree after reboot AP['%s']" % self.testbed.get_ap_mac_addr_by_sym_name(self.target_ap))
        self._testMeshTree()
        if self.passmsg: self.passmsg = "Mesh Tree reformed correct after reboot AP[%s]" % self.testbed.get_ap_mac_addr_by_sym_name(self.target_ap)

    def _testRebootZD(self):
        logging.info("Reboot Zone Director and verify Mesh Tree will not change after AP reboot")
        lib.zd.admin.reboot_zd(self.zd)
        tmethod8.pause_test_for(self.conf['check_status_timeout'], "Wait for the AP rejoin Zone Director")

        logging.info("Verify Mesh Tree after reboot Zone Director")
        self._testMeshTree()
        if self.passmsg: self.passmsg = "Mesh Tree reformed correct after reboot Zone Director"

