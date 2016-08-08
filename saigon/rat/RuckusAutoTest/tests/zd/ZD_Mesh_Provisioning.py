# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Description:
   Author: An Nguyen
   Email: nnan@s3solutions.com.vn

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
            'test_ap_model': model of the ap under testing
            'expected_process': testing process that we want to test with ap, includes:
                                'provisioning' : AP provisions through ethernet
                                'become root' : AP becomes Root after provisioning
                                'become mesh' : AP becomes Mesh after provisioning
   Result type: PASS/FAIL
   Results: PASS: If the expected process is successful
            FAIL: If the AP could not complete the expected process

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Disable Mesh on ZD before excuting the Root AP testing process
   2. Test:
       - Enable Mesh on ZD
       - Verify the testing process:
           + 'provisioning' testing:
              - verify if the Mesh configuration is applied on AP
           + 'become root' testing:
              - verify if the Mesh configuration is applied on AP
              - verify if AP becomes Root AP on the Zone Director
           + 'become mesh' testing:
              - disconnect AP from system
              - verify if the AP becomes MAP
              - verify if AP becomes Mesh AP on the Zone Director
   3. Cleanup:
       - Make sure all APs are Root APs in system with Mesh enabled

   How it is tested?
       -

"""

import os
import time
import logging
import re

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import Ratutils as utils

class ZD_Mesh_Provisioning(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {}
    def config(self, conf):
        self.conf = conf
        self.ap_model = conf['test_ap_model']
        self.mesh_essid = utils.make_random_string(32, 'alpha')
        self.mesh_passphrase = utils.make_random_string(63, 'alpha')
        self.uplink_aps = []

        # Config testbed for testing Mesh APs
        if self.conf['expected_process'].lower() in ['become mesh']:
            if self.testbed.model_to_mac_list[self.ap_model]:
                self.mesh_ap = self.testbed.model_to_mac_list[self.ap_model][0]
            # Uplinks ap list base on the APs have same model with the mesh ap under Zone Director control
                self.uplink_aps = self.testbed.model_to_mac_list[self.ap_model][1:]
            else:
                raise Exception('Could not find any AP[%s] on the testbed' % self.ap_model)
        # Configure testbed for testing Root APs
        else:
            if self.testbed.model_to_mac_list[self.ap_model]:
                self.root_ap = self.testbed.model_to_mac_list[self.ap_model][0]
            else:
                raise Exception('Could not find any AP[%s] on the testbed' % self.ap_model)

            # Disable Mesh on Zone Director if it is enabled
            if self.testbed.components['ZoneDirector'].get_mesh_cfg()['mesh_enable']:
                self.testbed.disable_mesh()

    def test(self):
        log_msg = 'Testing %s for AP[%s]' % (self.conf['expected_process'], self.ap_model)
        logging.info(log_msg)
        self.testbed.enable_mesh(self.mesh_essid, self.mesh_passphrase)
        # Test for Mesh APs
        if self.conf['expected_process'].lower() in ['become mesh']:
            return self._testMeshAP()
        # Test for Root APs
        else:
            return self._testRootAP()

    def cleanup(self):
        logging.info('Restore the mesh to original configuration')
        all_root_aps = self.testbed.mac_to_ap.keys()
        all_mesh_aps = []
        self.testbed.form_mesh(all_root_aps, all_mesh_aps)

    def _testMeshAP(self):
        if not self.uplink_aps:
            msg = 'There is no appropriate uplink AP (%s) in the system to complete Mesh provisioning' % self.ap_model
            raise Exception(msg)

        self.testbed.form_mesh(self.uplink_aps, [(self.mesh_ap, self.uplink_aps)])
        # Verify the Mesh configuration is applied on APs
        res, msg = self.testbed.verify_mesh_aps([(self.mesh_ap, self.uplink_aps)], self.mesh_essid, self.mesh_passphrase)
        if res == 'FAIL':
            return (res, msg)

        # Verify if the AP becomes Mesh on the Zone Director after provisioning
        ap_info = self.testbed.components['ZoneDirector'].get_all_ap_info(self.mesh_ap)
        if 'Mesh AP' not in ap_info['status']:
            msg = 'AP status on Zone Director is \'%s\' instead of \'Mesh AP\'' % ap_info['status']
            return ('FAIL', msg)
        else:
            return ('PASS', '')

    def _testRootAP(self):
        # Verify if the Mesh configuration is applied on the expected AP
        res, msg = self.testbed.verify_root_aps([self.root_ap], self.mesh_essid, self.mesh_passphrase)
        if res == 'FAIL' or self.conf['expected_process'] == 'provisioning':
            return (res, msg)

        # Verify if the AP becomes Root on the Zone Director after provisioning
        ap_info = self.testbed.components['ZoneDirector'].get_all_ap_info(self.root_ap)
        if 'Root AP' not in ap_info['status']:
            msg = 'AP status on Zone Director is \'%s\' instead of \'Root AP\'' % ap_info['status']
            return ('FAIL', msg)
        else:
            return ('PASS', '')

