# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Author: Thai Pham (pvthai@s3solutions.com.vn)

Description: ZD_Mesh_WebUI_Configuration Test class tests the ability of the Zone Director to configure mesh and
             releated information on its webUI. The ability to form the mesh network of the APs is also verified.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'model': 'AP model',
                    'topology': 'Mesh topology, possible values are root, or root-mesh',
                    'verify_ssid': 'a boolean value to indicate that mesh name needs to be verified',
                    'verify_passphrase': 'a boolean value to indicate that mesh psk needs to be verified',
   Result type: PASS/FAIL
   Results: PASS: If mesh can be enabled on the webUI, the APs can connect to the network as expected role,
                  and the information is shown on the webUI correctly.
            FAIL: if one of the above criteria is not satisfied

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Enable mesh on the ZD's webUI if it has not been done yet.
       - If the topology is root-mesh, reboot the mesh AP and disable the switch port connects it.
       - If 'verify_ssid' or 'verify_passphrase', make change to mesh configuration, then try to reconnect
         to the mesh AP (if there are some)
   2. Test:
       - Log on to each root AP and verify the WLAN list, the mesh name and passphrase, and the mesh links
       - Log on to each mesh AP and verify the WLAN list, the mesh name and passphrase, and the mesh links
   3. Cleanup:
       - If there are some mesh AP, reboot them and enable the appropriate switch ports. Make sure that they all
         become root AP.
"""

import os
import time
import logging
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import Ratutils as utils

class ZD_Mesh_WebUI_Configuration(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {'model': 'AP model',
                           'topology': 'Mesh topology, possible values are root, or root-mesh',
                           'verify_ssid': 'a boolean value to indicate that mesh name needs to be verified',
                           'verify_passphrase': 'a boolean value to indicate that mesh psk needs to be verified'}
    def config(self, conf):
        # Testing parameter
        if conf['verify_ssid']:
            self.mesh_name = utils.make_random_string(32, "alnum")
        else:
            self.mesh_name = ""

        if conf['verify_passphrase']:
            self.mesh_psk = utils.make_random_string(63, "alnum")
        else:
            self.mesh_psk = ""

        self.rap_list = None
        self.map_list = None
        self.rap_list, self.map_list = self.testbed.generate_ap_lists(conf['topology'], conf['model'])

        logging.info("Enable mesh on the Zone Director if it has not been done")
        self.testbed.enable_mesh()

        logging.info("Configure mesh network")
        self.testbed.form_mesh(self.rap_list, self.map_list)

        if self.mesh_name or self.mesh_psk:
            logging.info("Configure new mesh name or pass-phrase")
            self.testbed.enable_mesh(self.mesh_name, self.mesh_psk)

    def test(self):
        logging.info("Get current mesh configuration on the ZD and verify it")
        mesh_conf = self.testbed.components['ZoneDirector'].get_mesh_cfg()
        if not mesh_conf['mesh_enable']:
            logging.info("Incorrect mesh status: %s" % mesh_conf['mesh_enable'])
            return("FAIL", "Mesh configuration shown on ZD as 'disabled' after it had been configured")
        if self.mesh_name and mesh_conf['mesh_name'] != self.mesh_name:
            logging.info("Incorrect mesh name %s (should be %s)" % (mesh_conf['mesh_name'], self.mesh_name))
            return ("FAIL", "Mesh name shown on ZD was '%s' instead of '%s' after it had been configured" % \
                    (mesh_conf['mesh_name'], self.mesh_name))
        if self.mesh_psk and mesh_conf['mesh_psk'] != self.mesh_psk:
            logging.info("Incorrect mesh psk %s (should be %s)" % (mesh_conf['mesh_psk'], self.mesh_psk))
            return ("FAIL", "Mesh pass-phrase shown on ZD was '%s' instead of '%s' after it had been configured" % \
                    (mesh_conf['mesh_psk'], self.mesh_psk))

        logging.info("Verify the root APs")
        res, msg = self.testbed.verify_root_aps(self.rap_list, self.mesh_name, self.mesh_psk)
        if res == "FAIL":
            return (res, msg)

        logging.info("Verify the mesh APs")
        res, msg = self.testbed.verify_mesh_aps(self.map_list, self.mesh_name, self.mesh_psk)
        if res == "FAIL":
            return (res, msg)

        return ("PASS", "")

    def cleanup(self):
        self.testbed.cleanup_mesh_test_script()
