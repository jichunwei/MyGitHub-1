# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Author: Thai Pham (pvthai@s3solutions.com.vn)

Description: ZD_Mesh_WebUI_Neighbor_Status Test class tests the ability of the Zone Director and AP to display
             correct information about the neighbor APs.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
   Result type: PASS/FAIL
   Results: PASS: If it the information is shown correctly or synced between the AP and the ZD.
            FAIL: if one of the above criteria is not satisfied
   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Get current mesh configuration on the ZD.
       - If mesh has not been enabled then enable it
       - Form a mesh network according to the given 'topology'
   2. Test:
       - Go to the WebUI of the ZD and get the list of neighbor APs of the root AP
       - Login to CLI of the root AP and get mesh information
       - Verify each entry in the neighbor APs table and compare it against the mesh information
         on the AP.
       - Repeate the above 3 steps on the mesh AP if it exists
   3. Cleanup:
       - Restore the system to all root-AP setup.

"""

import re
import time
import logging
import math

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Debug as bugme

class ZD_Mesh_WebUI_Neighbor_Status(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {'model': 'AP model',
                           'topology': 'Mesh topology, possible values are root, or root-mesh'}

    def config(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        # Select the APs
        self.rap_list = None
        self.map_list = None
        self.rap_list, self.map_list = self.testbed.generate_ap_lists(conf['topology'], conf['model'])

        logging.info("Enable mesh on the Zone Director if it has not been done")
        self.testbed.enable_mesh()

        logging.info("Configure mesh network")
        self.testbed.form_mesh(self.rap_list, self.map_list)
        # Give time for the mesh information to be synced between the APs and the ZD
        time.sleep(15)

    def test(self):
        logging.info("Verify neighbor status of the root AP %s" % self.rap_list[0])
        #JLIN@20090307 add delay times for AP to scanning the neighbor APs
        timeout = 360
        base_time = time.time()
        while True:
            res, msg = self._verifyMeshNeighborStatus(self.rap_list[0])
            if res == "PASS": break
            logging.info("Verification fails")
            if time.time() - base_time > timeout:
                return (res, msg)
            time.sleep(5)
            logging.info("Give it another try")

        if self.map_list:
            logging.info("Verify neighbor status of the mesh AP %s" % self.map_list[0][0])
            base_time = time.time()
            while True:
                res, msg = self._verifyMeshNeighborStatus(self.map_list[0][0])
                if res == "PASS": break
                logging.info("Verification fails")
                if time.time() - base_time > timeout:
                    return (res, msg)
                time.sleep(5)
                logging.info("Give it another try")

        return ("PASS", "")

    def cleanup(self):
        self.testbed.cleanup_mesh_test_script()

    def _verifyMeshNeighborStatus(self, ap_mac):
        """
        Verify the status of the neighbors of the AP with given ap_mac
        The output shown on WebUI of ZD will be compared against the output from the AP's CLI
        @param ap_mac: MAC address of the target AP
        """
        logging.info("Get detail information of the AP %s shown on the ZD" % ap_mac)
        ap_info_on_zd = lib.zd.aps.get_ap_detail_neighbor_by_mac_addr(self.zd, ap_mac)
        # Make sure that the "Neighbor APs" table shows all other APs
        for mac in self.testbed.mac_to_ap.keys():
            if mac.lower() != ap_mac.lower():
                # The mac is not the target AP
                found = False
                for (neighbor_mac, neighbor_info) in ap_info_on_zd.iteritems():
                    if mac.lower() == neighbor_info['mac']:
                        found = True
                        break

                if not found:
                    return ("FAIL", "The AP %s was not shown in the 'Neighbor APs' table on ZD WebUI" % mac)

        logging.info("Get mesh information on the CLI of the AP %s" % ap_mac)
        mesh_info_on_cli = self.testbed.mac_to_ap[ap_mac.lower()].get_mesh_info_dict()

        # Define Filter to Label table
        filter_to_label_pattern = {}
        filter_to_label_pattern["c"] = "%d (Connected)"
        filter_to_label_pattern["r"] = "%d"
        filter_to_label_pattern["-"] = "%d"
        filter_to_label = {}
        filter_to_label["c"] = ""
        filter_to_label["r"] = ""
        filter_to_label["-"] = ""
        filter_to_label["a"] = "N/A (No APs in ACL)"
        filter_to_label["l"] = "N/A (Would form a loop)"
        filter_to_label[""] = "N/A (Unknown)"
        filter_to_label["z"] = "N/A (Zero bandwidth available)"
        filter_to_label["n"] = "N/A (Different radio type)"
        filter_to_label["d"] = "N/A (Exceeds max hop)"
        filter_to_label["f"] = "N/A (Exceeds max hop)"
        filter_to_label["s"] = "N/A (Not ready)"
        other_label = "N/A (No mesh-configured)"

        # Each line shown on the ZD should have a corresponding line on the AP's CLI
#        for neighbor_info_on_zd in ap_info_on_zd['neighbor']:
        logging.debug("Information of a neighbor: %s" % neighbor_info)
        neighbor_info_on_cli = None
        for (mac, mesh_link) in mesh_info_on_cli.iteritems():
            if mac == neighbor_info['mac'].lower():
                neighbor_info_on_cli = mesh_link
                break

        if not neighbor_info_on_cli:
            msg = "Not found information of the neighbor %s on the AP %s CLI" % (neighbor_info['mac'], ap_mac)
            return ("FAIL", msg)
        # The entry is found
        # Update the labels
        if neighbor_info_on_cli.has_key('P-Metric'):
            p_adver = neighbor_info_on_cli['P-Metric']
            
        else:
            p_adver = neighbor_info_on_cli['CalcUpl']
        
        filter_code = neighbor_info_on_cli['Flt']
        if filter_code in ["c", "r", "-"]:
            filter_to_label[filter_code] = filter_to_label_pattern[filter_code] % round(float(p_adver))
        # And verify the Filter code against the "uplink availability" on the ZD
        try:
            expected_text = filter_to_label[filter_code]
        except KeyError:
            expected_text = other_label
            
        if neighbor_info['mesh_uplink_rc'].lower() != expected_text.lower():
            msg = "The uplink availability of the neighbor %s shown on ZD" % neighbor_info['mac']
            msg += " was '%s' while the Filter code shown on CLI was" % neighbor_info['mesh_uplink_rc']
            msg += " '%c'. It should have been '%s'" % (filter_code, expected_text)
            return ("FAIL", msg)

        # Everything is fine
        return ("PASS", "")

