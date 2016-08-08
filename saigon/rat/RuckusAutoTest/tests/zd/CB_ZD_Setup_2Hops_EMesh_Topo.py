# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Sep 2010

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
        - mesh_tree: The expected mesh tree
        
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Base on the definition eMesh 2 hops topology to configure the L3Switch
        - Verify if the topology is formed correctly 
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS: If the eMesh topology is formed at expected
            FAIL: If could not forming the topology

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import Test_Methods as tmethod

from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Setup_2Hops_EMesh_Topo(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self.mconf = self._define_mesh_tree_conf(conf['mesh_tree'])
        self.zd = self.testbed.components['ZoneDirector']
        
    def test(self):
        res, msg = tmethod.emesh.test_forming_emesh_2_hops_network(**self.mconf)
        self._update_carrierbag()
        
        return self.returnResult(res, msg)
        
    def cleanup(self):
        pass
    
    def _define_mesh_tree_conf(self, conf):
        mconf = {'testbed': self.testbed,
                 'root_ap': self.testbed.get_ap_mac_addr_by_sym_name(conf['root_ap']),
                 'mesh_1_hop_ap': self.testbed.get_ap_mac_addr_by_sym_name(conf['mesh_1_hop_ap']),
                 'emesh_2_hops_aps': [self.testbed.get_ap_mac_addr_by_sym_name(ap) 
                                      for ap in conf['emesh_2_hops_aps']],}
    
        return mconf
    
    def _update_carrierbag(self):
        current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        self.carrierbag['expected_aps_info'] = current_aps_info