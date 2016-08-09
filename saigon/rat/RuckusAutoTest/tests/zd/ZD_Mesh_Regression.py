# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Description: Mesh Regression class to verify mesh functions work properly with 5.0Ghz radio frequency.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
        'active_ap'   : a symbolic name of active AP
        'ap_radio'    : radio frequency of active AP
        'mesh_ap'     : a symbolic name of mesh AP which connect to active AP when active AP is a RootAP
        'root_ap'     : a symbolic name of root AP which active AP connect to when active AP is a MAP
        'new_channel' : new mesh channel
   Result type: PASS/FAIL
   Results: PASS: MeshAP can join to RootAP after change channel or mesh ACL correctly.
            FAIL: if there is any verification step is fail

   Test procedure:
   1. Config:
      - Save current Active AP info
      - if test case is tuning mesh of active_ap is a MAP, form Mesh

   2. Test:
      - Change AP mesh channel and mesh ACL
      - Verify mesh AP able rejoin with RootAP

   3. Cleanup:
      - remove AP configuration applied in test functions

"""

import os
import re
import logging
import time

from RuckusAutoTest.tests.zd import libZD_TestConfig as tconfig
from RuckusAutoTest.tests.zd import libZD_TestMethods as tmethod
from RuckusAutoTest.tests.zd import libZD_TestMethods_v8 as tmethod8
from RuckusAutoTest.models import Test
from RuckusAutoTest.common import lib_Debug as bugme
from RuckusAutoTest.components import Helpers as lib

class ZD_Mesh_Regression(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = { 'active_ap'   : 'a symbolic name of active AP',
                            'ap_radio'    : 'radio frequency of active AP',
                            'mesh_ap'     : 'a symbolic name of mesh AP which connect to active AP when active AP is a RootAP',
                            'root_ap'     : 'a symbolic name of root AP which active AP connect to when active AP is a MAP',
                            'new_channel' : 'new mesh channel'
                           }

    def config(self, conf):
        self._cfgInitTestParams(conf)
        self._cfgGetActiveAP()
        self._cfgSaveCurrentAPConfig()

    def test(self):
        self._formMesh()
        if self.errmsg: return ('FAIL', self.errmsg)

        self.tc2f[self.conf['test_case']]()
        if self.errmsg: return ('FAIL', self.errmsg)
        self.passmsg = 'Mesh functions work properly'
        return ('PASS', self.passmsg)

    def cleanup(self):
        #self.zd.remove_all_cfg()
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        import lib_clean_up as cls
        cls.remove_all_cfg(self.zd, self.zdcli)

        self._restoreMesh()

#
# config()
#
    def _cfgInitTestParams(self, conf):
        self.conf = dict(check_status_timeout = 30,
                          active_ap = '',
                          test_case = '',
                          ap_radio = '',
                          root_ap = '',
                          mesh_ap = ''
                          )
        self.conf.update(conf)

        self.tc2f = {
            'change_channel': self._testChangeChannel,
            'tuning_mesh_acl': self._testTuningMeshACL,
        }

        self.zd = self.testbed.components['ZoneDirector']
        self.errmsg = ''
        self.passmsg = ''

    def _cfgGetActiveAP(self):
        if self.conf.has_key('active_ap'):
            self.active_ap = tconfig.get_testbed_active_ap(self.testbed, self.conf['active_ap'])
            if not self.active_ap:
                raise Exception("Active AP [%s] not found in the test bed" % self.conf['active_ap'])

            self.active_ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['active_ap'])

    def _formMesh(self):
        logging.info("Forming Mesh testbed with 1 RootAP and 1 MAP testing")
        if self.conf['root_ap']:
            root_ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['root_ap'])
            self.testbed.form_mesh([root_ap_mac], [(self.active_ap_mac, [root_ap_mac])])
        if self.conf['mesh_ap']:
            mesh_ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['mesh_ap'])
            self.testbed.form_mesh([self.active_ap_mac], [(mesh_ap_mac, [self.active_ap_mac])])


    def _cfgSaveCurrentAPConfig(self):
        logging.info("Save current active AP[%s] configure" % self.active_ap_mac)
        self.active_ap_cfg = lib.zd.ap.get_cfg_info_by_mac_addr(self.zd, self.active_ap_mac)


#
# test()
#

    def _testChangeChannel(self):
        logging.info("Change active AP [%s] channel to [%s]" % (self.active_ap_mac, self.conf['new_channel']))

        radio = {'5.0': 'na', '2.4': 'bg'}[self.conf['ap_radio']]
        lib.zd.ap.cfg_ap(self.zd, self.active_ap_mac, {'channel': self.conf['new_channel'], 'radio': radio})

        logging.info("Verify channel of active AP[%s]" % self.active_ap_mac)
        (meshu_channel, mode) = self.active_ap.get_channel("meshu", False)
        logging.debug("Meshu channel on AP: %s" % meshu_channel)
        (meshd_channel, mode) = self.active_ap.get_channel("meshd", False)
        logging.debug("Meshd channel on AP: %s" % meshd_channel)
        if str(meshu_channel) != self.conf['new_channel'] or str(meshd_channel) != self.conf['new_channel']:
            bugme.pdb.set_trace()
            self.errmsg = "New mesh channel did not applied to AP correctly"

    def _testTuningMeshACL(self):
        logging.info("Verify Mesh AP join to correct RootAP")
        active_ap_info = lib.zd.aps.get_ap_detail_mesh_tree_by_mac_addr(self.zd, self.active_ap_mac)
        root_ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['root_ap'])

        if active_ap_info['uplink']['ap'] != root_ap_mac:
            self.errmsg = "Mesh AP join to wrong RootAP"


# cleanup()
#
    def _restoreMesh(self):
        if self.conf['root_ap']:
            self.testbed.form_mesh([self.active_ap_mac], [])
        if self.conf['mesh_ap']:
            mesh_ap_mac = self.testbed.get_ap_mac_addr_by_sym_name(self.conf['mesh_ap'])
            self.testbed.form_mesh([mesh_ap_mac], [])

