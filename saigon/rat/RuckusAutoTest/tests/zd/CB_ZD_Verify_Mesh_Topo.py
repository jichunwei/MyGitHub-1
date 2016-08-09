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
   
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Verify if the mesh tree are match with expected 
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS: If the mesh tree is not changed
            FAIL: If the mesh tree is changed

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
from pprint import pformat

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_Verify_Mesh_Topo(Test):
    required_components = ['Station', 'RuckusAP', 'ZoneDirector']
    parameter_description = {
                            }

    def config(self, conf):
        self._init_test_parameter()

    def test(self):
        res, msg = self._verify_aps_info()
        
        return self.returnResult(res, msg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self):
        self.zd = self.testbed.components['ZoneDirector']
    
    def _verify_aps_info(self):
        expected_aps_info = self.carrierbag['expected_aps_info']
        logging.debug('The expected APs info:\n %s' % pformat(expected_aps_info))
        current_aps_info = lib.zd.ap.get_all_ap_info(self.zd)
        logging.debug('The current APs info: \n %s' % pformat(current_aps_info))
        
        errmsg = ''
        passmsg = 'The current APs info %s \n is match with the expected' % pformat(current_aps_info)
        
        lost_aps = []
        error_aps = []
        for mac_addr in expected_aps_info.keys():
            if mac_addr not in current_aps_info.keys():
                lost_aps.append(mac_addr)
                continue
            if current_aps_info[mac_addr]['status'] != expected_aps_info[mac_addr]['status']:
                error_aps.append(mac_addr)
                continue
        
        if lost_aps:
            errmsg = 'There are APs %s lost.' % lost_aps 
        if error_aps:
            errmsg += 'The APs %s have the information is not match with expected' % error_aps 
        
        if errmsg:
            return ('FAIL', errmsg)
        
        return ('PASS', passmsg)
        
