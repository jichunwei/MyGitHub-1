# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Feb 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 
   Test parameters:    
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Compare guest restricted ipv6 access between GUI get and CLI get
                
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Data between gui get and cli get are same
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib


class CB_ZD_Verify_Guest_Restricted_IPV6_Access_GUI_CLI_Get(Test):
    '''
    create the guest restricted subnet access on zd
    '''
    required_components = []
    parameter_description = {}
    
    def config(self, conf):
        self._init_test_params(conf)
        
    def test(self):
        try:
            logging.info("Compare guest restricted ipv6 access between GUI get and CLI get")
            res_access_list = lib.zdcli.guest_access.verify_restricted_ipv6_access_gui_cli_get(self.gui_get_ipv6_access_list, self.cli_restricted_ipv6_access_dict)
            
            if res_access_list:
                self.errmsg = "Data between GUI get and CLI get are different: %s" % res_access_list
            
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
        self.conf = {}
        self.conf.update(conf)
        
        self.gui_get_ipv6_access_list = self.carrierbag['gui_restricted_ipv6_access_list']
        self.cli_restricted_ipv6_access_dict = self.carrierbag['cli_restricted_ipv6_access_dict']
        
        self.errmsg = ''
        self.passmsg = ''
    
    def _update_carrier_bag(self):
        pass  