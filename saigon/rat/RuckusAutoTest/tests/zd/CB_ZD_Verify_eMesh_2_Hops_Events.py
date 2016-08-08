# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: This script support to verify if the eMesh forming message correct
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
        - Base on current mesh tree verify if the eMesh forming message is showed 
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.tests.zd import Test_Methods as tmethod

from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_Verify_eMesh_2_Hops_Events(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter()

    def test(self):
        logging.info('Detect the current mesh tree:')
        mtree = tmethod.emesh.detect_mesh_tree(lib.zd.ap.get_all_ap_info(self.zd).values())
        logging.info('\n %s' % pformat(mtree, 4, 50))
        
        res, msg = tmethod.emesh.verify_emesh_2hops_forming_event(self.zd, mtree['connected'])   
        return self.returnResult(res, msg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self):
        self.zd = self.testbed.components['ZoneDirector']