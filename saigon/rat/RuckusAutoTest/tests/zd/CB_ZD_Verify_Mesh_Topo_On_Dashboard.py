# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: Verify the mesh tree in mesh summary table in DashBoard page
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Sep 2010

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
   
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Verify if the mesh tree on the DashBoard is match with the expected topology from Monitor page.  
    3. Cleanup:
        -
        
   Result type: PASS/FAIL
   Results: PASS: If the mesh tree is match
            FAIL: If the info in Monitor page and DashBoard page are not same 

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
import time
from copy import deepcopy
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import Test_Methods as tmethod

from RuckusAutoTest.common import lib_Debug as bugme


class CB_ZD_Verify_Mesh_Topo_On_Dashboard(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                             }

    def config(self, conf):
        self._init_test_params(conf)

    def test(self):
        expected_mtree = self._detect_expected_mesh_tree()['connected']
        logging.info('Expected mesh tree: \n %s' % pformat(expected_mtree, 4, 100))
        
        mtree_from_dboard = self._detect_mesh_tree_from_dashboard()
        logging.info('Expected mesh tree: \n %s' % pformat(mtree_from_dboard, 4, 100))
        
        if mtree_from_dboard != expected_mtree:
            errmsg = 'The mesh tree from dash board is %s instead of %s' 
            errmsg = errmsg % (mtree_from_dboard, expected_mtree)
            return self.returnResult("FAIL", errmsg)
        
        passmsg = 'The mesh tree from dash board is correct as expected %s' % expected_mtree
        return self.returnResult("PASS", passmsg)

    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        
        if self.carrierbag.has_key('expected_aps_info'):
            self.expected_aps_info = self.carrierbag['expected_aps_info'].copy()
        else:
            self.expected_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
            
    def _detect_expected_mesh_tree(self):
        return tmethod.emesh.detect_mesh_tree(self.expected_aps_info.values())
    
    def _detect_mesh_tree_from_dashboard(self):
        lib.zd.dboard.add_mesh_topology_widget_to_dashboard(self.zd)
        time.sleep(5)        
        return lib.zd.dboard.detect_mesh_tree(self.zd, self.expected_aps_info.keys())
