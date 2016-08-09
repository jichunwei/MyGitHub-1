# Copyright (C) 2008 Ruckus Wireless, Inc. All rights reserved.

"""
Author: Thai Pham (pvthai@s3solutions.com.vn)

Description: ZD_Mesh_WebUI_Setup_Wizard Test class tests the ability of the Zone Director to run set up wizard
             and enable mesh.

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
   Result type: PASS/FAIL
   Results: PASS: If ZD can run set up wizard and enable mesh
            FAIL: If it fails to run setup wizard

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied

   Test procedure:
   1. Config:
       -
   2. Test:
       - Record the list of connected APs
       - Restore the ZD's configuration to factory default
       - Run the set up wizard, enable mesh when asked
       - Verify that all the APs connect to the ZD and run mesh
   3. Cleanup:
       -
"""

import os
import time
import logging
import re
import pdb

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Station
from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.common import Ratutils as utils
from RuckusAutoTest.components.lib.zd import te_mgmt_vlan_hlp as TE
from RuckusAutoTest.components import NetgearSwitchRouter as NSR
from RuckusAutoTest.tests.zd.lib import test_methods_emesh as tmethod

class ZD_Mesh_WebUI_Setup_Wizard(Test):
    required_components = ['RuckusAP', 'ZoneDirector']
    parameter_description = {}
    def config(self, conf):
        self.mesh_name = utils.make_random_string(32, "alnum")
        self.mesh_psk = utils.make_random_string(63, "alnum")
        self.rap_list = self.testbed.mac_to_ap.keys()
        self.map_list = []
        self.conf = conf
        if self.conf.has_key('debug'): pdb.set_trace()
        self.zd = self.testbed.components['ZoneDirector']
        self.mgmt_vlan = TE.MVLAN.get_node_mgmt_vlan_info(self.zd) if self.zd.has_mgmt_vlan else {}
        # Record current configuration of the APs
        self.all_aps_config = {}
        for mac in self.testbed.mac_to_ap.keys():
            logging.info("Record current configuration of the AP %s on the ZD" % mac)
            self.all_aps_config[mac] = self.zd.get_ap_cfg(mac)
            self.all_aps_config[mac]['mesh_uplink_aps'] = []

        logging.info("Configure mesh network to all-root topology")

        # Modified by Serena Tan. 2010.11.09
        # To fix bug 16316.
#        self.testbed.form_mesh(self.rap_list, self.map_list)
        self._set_all_aps_to_root()

        self._store_mgmt_vlan_info()
        
    def test(self):
        if self.conf.has_key('debug'): pdb.set_trace()
        # Set configuration on the APs to factory default
        for mac, ap in self.testbed.mac_to_ap.iteritems():
            logging.info("Set configuration on the AP %s to factory default" % mac)
            ap.set_factory()
            ap.reboot(login = False)
            ap.close()

        # Reset factory and run the setup wizard
        logging.info("Set configuration of the ZD to factory default and run the set up wizard")
        conf = {'mesh_name':self.mesh_name, 'mesh_passphrase':self.mesh_psk, 'mesh_enabled':True}
        self.zd.do_login()
        self._reset_factory_and_untag_zd_switch_port()
        self.zd._setup_wizard_cfg(new_conf = conf)
        self._restore_mgmt_vlan_info()
        #self.testbed.components['ZoneDirector'].setup_wizard_cfg(new_conf=conf)
        time.sleep(120)

        logging.info("Make sure that all APs connect back to the ZD and show up as RootAPs")
        start_time = time.time()
        timeout = 600
        while True:
            all_done = True
            all_aps_info = self.zd.get_all_ap_info()
            if len(all_aps_info) != len(self.testbed.mac_to_ap):
                all_done = False
            else:
                for ap_info in all_aps_info:
                    if ap_info['status'] != "Connected (Root AP)":
                        all_done = False
                        break
            if all_done: break
            if time.time() - start_time > timeout:
                raise Exception("The APs didn't show up on the ZD correctly after %s seconds" % timeout)
            time.sleep(15)

        logging.info("Get current mesh configuration on the ZD and verify it")
        mesh_conf = self.zd.get_mesh_cfg()
        if not mesh_conf['mesh_enable']:
            logging.info("Incorrect mesh status: %s" % mesh_conf['mesh_enable'])
            return("FAIL", "Mesh configuration shown on ZD as 'disabled' after it had been configured")
        if mesh_conf['mesh_name'] != self.mesh_name:
            logging.info("Incorrect mesh name %s (should be %s)" % (mesh_conf['mesh_name'], self.mesh_name))
            return ("FAIL", "Mesh name shown on ZD was '%s' instead of '%s' after it had been configured" % \
                    (mesh_conf['mesh_name'], self.mesh_name))
        if mesh_conf['mesh_psk'] != self.mesh_psk:
            logging.info("Incorrect mesh psk %s (should be %s)" % (mesh_conf['mesh_psk'], self.mesh_psk))
            return ("FAIL", "Mesh pass-phrase shown on ZD was '%s' instead of '%s' after it had been configured" % \
                    (mesh_conf['mesh_psk'], self.mesh_psk))

        logging.info("Verify the APs")
        res, msg = self.testbed.verify_root_aps(self.rap_list, self.mesh_name, self.mesh_psk)
        if res == "FAIL":
            return (res, msg)

        return ("PASS", "")

    def cleanup(self):
        # Restore channel and txpower of the APs on the ZD
        for mac, ap_cfg in self.all_aps_config.iteritems():
            logging.info("Restore configuration of the AP %s on the ZD" % mac)
            self.zd.set_ap_cfg(ap_cfg)

    def _store_mgmt_vlan_info(self):
        if self.mgmt_vlan:
            logging.info("MgmtVlan installed; gather its information")
            # if L3Switch not presented; let the test fail anyway
            self.l3sw = self.testbed.components['L3Switch']
            # Can python's class initialized from its parent instance?
            nsr_conf = dict(ip_addr = self.l3sw.ip_addr, username = self.l3sw.username,
                            password = self.l3sw.password, enable_password = self.l3sw.enable_password)
            self.nsr = NSR.NetgearSwitchRouter(nsr_conf)
            self.mgmt_vlan['swp'] = TE.get_zd_switch_port(self.zd, self.nsr)
            logging.info("MgmtVlan attrs: %s" % str(self.mgmt_vlan))

    def _reset_factory_and_untag_zd_switch_port(self):
        self.wait_for_alive = False if self.mgmt_vlan and self.mgmt_vlan['zd']['enabled'] else True
        # ZoneDirector._reset_factory() changed to not wait for ZD come alive
        # if ZD MgmtVlan is enabled.
        self.zd._reset_factory(self.wait_for_alive)
        if not self.wait_for_alive:
            # ZD port is tagged; after reset_factory; the port need to be untagged
            TE.NSRHLP.untag_switch_vlan_interface(self.nsr,
                                               self.mgmt_vlan['swp']['vlan_id'],
                                               self.mgmt_vlan['swp']['interface'],)
            # ATTN: step to reset_factoryWaitForAlive() immeidately
            try:
                # ZD is being reset and restarted
                self.zd._reset_factory_wait_for_alive_s1()
            except:
                # ZD is restarted
                self.zd._reset_factory_wait_for_alive_s2()

    def _restore_mgmt_vlan_info(self):
        if self.mgmt_vlan:
            if self.mgmt_vlan['zd']['enabled']:
                self.mgmt_vlan2 = TE.tag_zd_mgmt_vlan(self.zd,
                                                  self.nsr,
                                                  self.mgmt_vlan['swp']['interface'],
                                                  self.mgmt_vlan['swp']['vlan_id'],)
                time.sleep(2)
            ap_mgmt_vlan = self.mgmt_vlan['ap']['mgmt_vlan']
            if ap_mgmt_vlan['enabled'] and ap_mgmt_vlan['vlan_id']:
                if self.mgmt_vlan['ap']['zd_discovery']['enabled']:
                    prim_ip = self.mgmt_vlan['ap']['zd_discovery']['prim_ip']
                    sec_ip = self.mgmt_vlan['ap']['zd_discovery']['sec_ip']
                else:
                    prim_ip = sec_ip = u''
                self.appolicy2 = TE.tag_ap_mgmt_vlan(self.zd,
                                                  ap_mgmt_vlan['vlan_id'],
                                                  prim_ip, sec_ip)
    
    # Added by Serena Tan. 2010.11.09
    def _set_all_aps_to_root(self):
        tmethod.test_all_aps_become_root(**{'testbed': self.testbed})
