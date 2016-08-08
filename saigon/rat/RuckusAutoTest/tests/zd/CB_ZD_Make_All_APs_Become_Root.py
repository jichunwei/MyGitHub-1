# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: This script support to test forcing all APs in test bed be come root with ZD_Stations configuration.  
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Sep 2010

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'RuckusAP', 'ZoneDirector'
   Test parameters:
   
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Forming the test that configure the L3SWitch to make all APs reconnect ZD as ROOT.   
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS: If all APS become ROOT
            FAIL: If there is any exception or not all APS become ROOT

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import Test_Methods as tmethod

from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Make_All_APs_Become_Root(Test):
    required_components = ['ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self.mconf = self._define_mesh_tree_conf()
        self.zd = self.testbed.components['ZoneDirector']
        
    def test(self):
        res, msg = tmethod.emesh.test_all_aps_become_root(**self.mconf)
        self._update_carrierbag()
        
        return self.returnResult(res, msg)
        
    def cleanup(self):
        pass
    
    def _define_mesh_tree_conf(self):
        mconf = {'testbed': self.testbed,
                }
    
        return mconf
    
    def _update_carrierbag(self):
        current_aps_info = lib.zd.aps.get_all_ap_briefs(self.zd)
        self.carrierbag['expected_aps_info'] = current_aps_info