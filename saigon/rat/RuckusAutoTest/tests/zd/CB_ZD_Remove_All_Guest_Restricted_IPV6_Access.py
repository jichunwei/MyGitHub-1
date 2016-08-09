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
        - Remove all guest restricted ipv6 access via ZD GUI
                
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Remove all guest restricted ipv6 access via ZD GUI successfully
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga

class CB_ZD_Remove_All_Guest_Restricted_IPV6_Access(Test):
    '''
    create the guest restricted subnet access on zd
    '''
    required_components = ['ZoneDirector']
    parameter_description = {}
    
    def config(self, conf):
        self._init_test_params(conf)
        
    def test(self):
        self._remove_all_restricted_ipv6_access_list()
                
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self.passmsg = "Remove all guest restricted ipv6 access successfully."
            logging.info(self.passmsg)
            self._update_carrier_bag()
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    
    def _update_carrier_bag(self):
        pass     
    
    def _remove_all_restricted_ipv6_access_list(self):
        try:
            ga.remove_all_restricted_subnet_entries_ipv6(self.zd)
        except Exception, ex:
            self.errmsg = 'Remove all guest restricted ipv6 access list failed: %s' % ex.message