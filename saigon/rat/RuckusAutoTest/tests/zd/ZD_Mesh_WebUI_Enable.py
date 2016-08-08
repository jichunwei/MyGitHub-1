# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description: ZD_Mesh_WebUI_Enable Test class tests the ability of the Zone Director to enable mesh on its WebUI.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
   Result type: PASS/FAIL
   Results: PASS: If it is unable to enable mesh in the WebUI, or some of the AP cannot connect to the ZD as RootAP.
            FAIL: if one of the above criteria is not satisfied
   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Get current mesh configuration on the ZD.
       - If mesh has been enabled, disable it by doing a factory reset.
   2. Test:
       - Enable mesh on the ZD.
       - Verify the status of all connected APs to make sure that they all become Root AP
   3. Cleanup:

"""

import os
import time
import logging
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import Ratutils as utils

class ZD_Mesh_WebUI_Enable(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = { }
    def config(self, conf):
        self.mesh_name = utils.make_random_string(32, "alnum")
        self.mesh_psk = utils.make_random_string(63, "alnum")
        self.root_aps = self.testbed.mac_to_ap.keys()
        self.mesh_aps = []

        logging.info("Get current mesh configuration on the ZD")
        mesh_conf = self.testbed.components['ZoneDirector'].get_mesh_cfg()

        if mesh_conf['mesh_enable']:
            logging.info("Disable mesh on the Zone Director")
            self.testbed.disable_mesh()

    def test(self):
        logging.info("Enable mesh on the ZoneDirector")
        self.testbed.enable_mesh(self.mesh_name, self.mesh_psk)

        logging.info("Configure mesh network")
        self.testbed.form_mesh(self.root_aps, self.mesh_aps)

        logging.info("Get current mesh configuration on the ZD and verify it")
        mesh_conf = self.testbed.components['ZoneDirector'].get_mesh_cfg()
        logging.debug("Mesh config: %s" % mesh_conf)
        if not mesh_conf['mesh_enable']:
            logging.info("Incorrect mesh status: %s" % mesh_conf['mesh_enable'])
            raise Exception("Mesh configuration shown on ZD as 'disabled' after it had been configured")
        if mesh_conf['mesh_name'] != self.mesh_name:
            logging.info("Incorrect mesh name %s (should be %s)" % (mesh_conf['mesh_name'], self.mesh_name))
            return ("FAIL", "Mesh name shown on ZD was '%s' instead of '%s' after it had been configured" % \
                    (mesh_conf['mesh_name'], self.mesh_name))
        if mesh_conf['mesh_psk'] != self.mesh_psk:
            logging.info("Incorrect mesh psk %s (should be %s)" % (mesh_conf['mesh_psk'], self.mesh_psk))
            return ("FAIL", "Mesh pass-phrase shown on ZD was '%s' instead of '%s' after it had been configured" % \
                    (mesh_conf['mesh_psk'], self.mesh_psk))

        return ("PASS", "")

    def cleanup(self):
        pass
