# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Oct 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector'
   Test parameters:
       - 'restricted_ipv6_access_list': 'restricted ipv6 access will be set',    
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Set guest restricted ipv6 access via ZD GUI
        - Get all guest restricted ipv6 access via ZD GUi
        - Compare data between set and get
                
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Configure guest ipv6 access successfully and data are same between set and get
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import guest_access_zd as ga

class CB_ZD_Set_Guest_Restricted_IPV6_Access(Test):
    '''
    create the guest restricted subnet access on zd
    '''
    required_components = ['ZoneDirector']
    parameter_description = {'restricted_ipv6_access_list': 'restricted ipv6 access will be set',
                             }
    
    def config(self, conf):
        self._init_test_params(conf)
    
        
    def test(self):
        try:
            logging.info("Configure guest restricted ipv6 access on ZD")
            ga.create_restricted_subnet_entries_ipv6(self.zd, self.restricted_ipv6_access_list)
            
            logging.info("Get All guest restricted ipv6 access on ZD")
            self.current_restricted_ipv6_access_list = ga.get_all_restricted_subnet_entries_ipv6(self.zd)
                    
            logging.info("Compare guest restricted ipv6 access between set and get")
            res_compare = ga.verify_restricted_ipv6_access_gui_set_get(self.restricted_ipv6_access_list, self.current_restricted_ipv6_access_list)
            
            if res_compare:
                self.errmsg = "Data between GUI Set and Get are different: %s" % res_compare
        except Exception, ex:
            self.errmsg = "Exception: %s" % ex.message
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self.passmsg = "Configure the guest restricted ipv6 access successfully."
            logging.info(self.passmsg)
            self._update_carrier_bag()
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'restricted_ipv6_access_list': []}
        self.conf.update(conf)
        
        self.restricted_ipv6_access_list = self.conf['restricted_ipv6_access_list']
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    
    def _update_carrier_bag(self):
        self.carrierbag['gui_restricted_ipv6_access_list'] = self.restricted_ipv6_access_list