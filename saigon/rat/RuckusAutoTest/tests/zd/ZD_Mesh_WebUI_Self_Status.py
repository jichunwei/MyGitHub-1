# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used
# in report generation.

"""
Description: ZD_Mesh_WebUI_Self_Status Test class tests the ability of the ZD
             to display correct status of the connected APs when mesh is enabled.

   Prerequisite (Assumptions about the state of the testbed/DUT):
            Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'

   Test parameters: 'model': 'AP model',

   Result type: PASS/FAIL
   Results:
        PASS: If the status of the APs are displayed correctly.
        FAIL: If one of the above criteria is not satisfied

   Messages:
       If FAIL the test script returns a message related to the criterion
       that is not satisfied

   Test procedure:
   1. Config:
       - Enable mesh on the ZD's webUI if it has not been done yet.
       - Setup the system according to 'root-mesh' topology.
   2. Test:
       - Login to the ZD's webUI and get detail information of the root and mesh APs.
       - Verify the status of the root AP and the Downlinks table
       - Verify the status of the mesh AP and the Uplink table
   3. Cleanup:
       - Restore to the default setup with all root APs.
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import Ratutils as utils

class ZD_Mesh_WebUI_Self_Status(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {'model': 'AP model'}

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        # Testing parameter
        self.mesh_name = utils.make_random_string(32, "alnum")
        self.mesh_psk = utils.make_random_string(63, "alnum")

        # Select the APs
        self.rap_list = None
        self.map_list = None
        self.rap_list, self.map_list = self.testbed.generate_ap_lists("root-mesh", conf['model'])

        logging.info("Enable mesh on the Zone Director if it has not been done")
        self.testbed.enable_mesh(self.mesh_name, self.mesh_psk)

        logging.info("Configure mesh network")
        self.testbed.form_mesh(self.rap_list, self.map_list)

    def test(self):
        root_ap_mac = self.rap_list[0]
        mesh_ap_mac = self.map_list[0][0]

        # Verify the detail information of the Root AP
        logging.info("Get detail information of the RootAP %s shown on the \
                     ZD webUI and verify it" % root_ap_mac)
        ap_detail_info = lib.zd.aps.get_ap_detail_info_by_mac_addr(self.zd, root_ap_mac)
        ap_detail_mesh_tree = lib.zd.aps.get_ap_detail_mesh_tree_by_mac_addr(self.zd, root_ap_mac)


        if ap_detail_info['status'] != "Connected (Root AP)":
            msg = "The current status of the AP %s was '%s' instead of '%s'" % \
                  (root_ap_mac, ap_detail_info['status'], "Connected (Root AP)")
            return ("FAIL", msg)

        if len(ap_detail_mesh_tree['downlink']) == 0:
            msg = "The downlink table of the Root AP %s was empty" % root_ap_mac
            return ("FAIL", msg)

        found = False
        for dl_ap_info in ap_detail_mesh_tree['downlink'].iterkeys():
            if dl_ap_info.lower() == mesh_ap_mac.lower():
                found = True
                break

        if not found:
            msg = "There was no AP with MAC %s shown on the 'Downlinks' table" % mesh_ap_mac
            return ("FAIL", msg)

        # Verify the detail information of the Mesh AP
        logging.info("Get detail information of the MeshAP %s shown on the \
                     ZD webUI and verify it" % mesh_ap_mac)
        ap_detail_info = lib.zd.aps.get_ap_detail_info_by_mac_addr(self.zd, mesh_ap_mac)
        ap_detail_mesh_tree = lib.zd.aps.get_ap_detail_mesh_tree_by_mac_addr(self.zd, mesh_ap_mac)

        if ap_detail_info['status'] != "Connected (Mesh AP, 1 hop)":
            msg = "The current status of the AP %s was '%s' instead of '%s'" % \
                  (mesh_ap_mac, ap_detail_info['status'], "Connected (Mesh AP, 1 hop)")
            return ("FAIL", msg)

        if not ap_detail_mesh_tree['uplink']:
            msg = "There was no information about uplink AP shown on the detail \
                  information page of the AP %s" % mesh_ap_mac
            return ("FAIL", msg)

        if ap_detail_mesh_tree['uplink']['ap'].lower() != root_ap_mac.lower():
            msg = "The uplink AP was %s instead of %s in the detail information page \
                  of the AP %s" % (ap_detail_mesh_tree['uplink']['ap'],
                                   root_ap_mac, mesh_ap_mac)
            return ("FAIL", msg)

        return ("PASS", "")

    def cleanup(self):
        self.testbed.cleanup_mesh_test_script()
