# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Feb 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:    
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get all l3 ipv6 acls via ZD GUI.
                
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Get l3 ipv6 acls via ZD GUI successfully
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Get_L3_ACLs_IPV6(Test):
    required_components = ['ZoneDirector']
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        logging.info("Get L3/4/IPv6 address Access Control via GUI")
        self.current_l3_acls_ipv6 = lib.zd.ac.get_all_l3_ipv6_acl_cfgs(self.zd)
        
        if self.errmsg:
            return ('FAIL', self.errmsg)
        else:
            self.passmsg = 'Get L3 IPV6 ALCs from GUI successfully'
            self._update_carrier_bag()
            return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        args = dict()
        args.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrier_bag(self):
        self.carrierbag['existing_l3_ipv6_acls'] = self.current_l3_acls_ipv6