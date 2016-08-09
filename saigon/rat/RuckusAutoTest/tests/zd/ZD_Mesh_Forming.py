# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following class docstring is accurate since it will be used in report generation.

"""
Author: Thai Pham (pvthai@s3solutions.com.vn)

Description: ZD_Mesh_Forming test class tests the ability of the Zone Director to instruct the APs of different
             models to form mesh topologies. It also verifies if the APs using different radio cannot form mesh
             with each other.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters: 'rap_model': 'Root AP model',
                    'map_model': 'Mesh AP model',
                    'topology': 'Mesh topology, possible values: root-mesh',
                    'channelization': 'Channelization value when ap model is zf7942'
   Result type: PASS/FAIL
   Results: PASS: If the models of root AP and mesh AP are the same, they must form mesh. Otherwise, they can't.
            FAIL: If the models of the APs are the same, they can't form mesh. Or they can form mesh if they use
                  different radio.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       - Enable mesh on the ZD's webUI if it has not been done yet.
   2. Test:
       - Configure the APs to form mesh.
       - Verify their status shown on the ZD
       - Verify the connection to the APs after that.
   3. Cleanup:
       - If some of the mesh APs are not reachable or dead. Try to recover them by enabling the switch port
         connected to them.

"""

import os
import time
import logging
import re

from RuckusAutoTest.models import Test

class ZD_Mesh_Forming(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {'rap_model': 'Root AP model',
                           'map_model': 'Mesh AP model',
                           'topology': 'Mesh topology, possible values: root-mesh',
                           'channelization': 'Channelization value when ap model is zf7942'}
    def config(self, conf):
        # Testing parameter
        self.rap_model = conf['rap_model'].lower()
        self.map_model = conf['map_model'].lower()
        self.channelization = conf['channelization']
        self.topology = conf['topology'].lower()
        self.ap_cfg = {}
        if not re.match("^root(-mesh)+$", self.topology):
            raise Exception("Topology '%s' is unknown or unsupported" % self.topology)

        self.rap_list = []
        self.map_list = []

        roles = self.topology.split("-")
        if self.rap_model == self.map_model:
            ap_macs = self.testbed.model_to_mac_list[self.rap_model]
            if len(ap_macs) < len(roles):
                msg = "Not enough AP of model '%s' to build the topology '%s'" % (self.rap_model, self.topology)
                raise Exception(msg)

            self.rap_list.append(ap_macs[0])

            idx = 1
            while idx < len(roles):
                self.map_list.append((ap_macs[idx], [ap_macs[idx - 1]]))
                idx += 1

            if self.channelization:
                logging.info("Record current configuration of the APs that are under test")
                for ap_info in self.rap_list:
                    self.ap_cfg[ap_info] = self.testbed.components['ZoneDirector'].get_ap_cfg(ap_info)

                for ap_info in self.map_list:
                    ap_mac = ap_info[0]
                    self.ap_cfg[ap_mac] = self.testbed.components['ZoneDirector'].get_ap_cfg(ap_mac)

                logging.info("Set their channelization to '%s'" % self.channelization)
                for cfg in self.ap_cfg.values():
                    tmp_cfg = cfg.copy()
                    tmp_cfg['channelization'] = self.channelization
                    tmp_cfg['channel'] = '6'
                    self.testbed.components['ZoneDirector'].set_ap_cfg(tmp_cfg)

                logging.info("Try to recover the connection to all the APs if they were disconnected")
                timeout = 600
                start_time = time.time()
                for ap in self.testbed.mac_to_ap.values():
                    while True:
                        if time.time() - start_time > timeout: break
                        try:
                            ap.verify_component()
                            break

                        except:
                            time.sleep(5)

            # End of if self.channelization

        # End of if self.rap_model == self.map_model

        else:
            # Negative tests
            if len(roles) > 2:
                raise Exception("Unsupported topology '%s'" % self.topology)

            if not self.testbed.model_to_mac_list[self.rap_model]:
                raise Exception("There was not enough AP of model to perform the test" % self.rap_model)

            self.rap_list.append(self.testbed.model_to_mac_list[self.rap_model][0])

            if not self.testbed.model_to_mac_list[self.map_model]:
                raise Exception("There was not enough AP of model to perform the test" % self.map_model)

            self.map_list.append((self.testbed.model_to_mac_list[self.map_model][0], [self.rap_list[0]]))

        logging.info("Enable mesh on the Zone Director if it has not been done")
        self.testbed.enable_mesh()


    def test(self):
        if self.rap_model == self.map_model:
            logging.info("Try to form mesh of APs of model '%s'" % self.rap_model)
            self.testbed.form_mesh(self.rap_list, self.map_list)

            logging.info("Get current mesh configuration on the ZD and verify it")
            mesh_conf = self.testbed.components['ZoneDirector'].get_mesh_cfg()

            logging.info("Verify the root APs")
            res, msg = self.testbed.verify_root_aps(self.rap_list, mesh_conf['mesh_name'], mesh_conf['mesh_psk'])
            if res == "FAIL":
                return (res, msg)

            logging.info("Verify the mesh APs")
            res, msg = self.testbed.verify_mesh_aps(self.map_list, mesh_conf['mesh_name'], mesh_conf['mesh_psk'])
            if res == "FAIL":
                return (res, msg)

        else:
            # Negative test
            try:
                logging.info("Try to form mesh of APs of model '%s' and model '%s'" % (self.rap_model, self.map_model))
                self.testbed.form_mesh(self.rap_list, self.map_list, 300)

                for mesh_ap_info in self.map_list:
                    mesh_ap_mac = mesh_ap_info[0]
                    logging.info("Try to verify the connection to the mesh AP %s" % mesh_ap_mac)
                    self.testbed.mac_to_ap[mesh_ap_mac].verify_component()

                msg = "It was able to form mesh between '%s' and '%s'" % (self.rap_model, self.map_model)
                logging.info(msg)
                return ("FAIL", msg)

            except:
                logging.info("It was unable to form mesh between '%s' and '%s'" % (self.rap_model, self.map_model))

        return ("PASS", "")


    def cleanup(self):
        self.testbed.cleanup_mesh_test_script()

        for mac, cfg in self.ap_cfg.iteritems():
            logging.info("Restore configuration of the AP %s on the ZD" % mac)
            self.testbed.components['ZoneDirector'].set_ap_cfg(cfg)

