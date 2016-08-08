# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: Feb 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirectorCLI'
   Test parameters:    
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Get all guest restricted ipv6 access list via ZD CLI.
                
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Get guest restricted ipv6 access list successfully
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_CLI_Get_Guest_Restrict_Access_IPV6(Test):
    required_components = ['ZoneDirectorCLI']
    test_parameters = {}

    def config(self, conf):
        self._init_test_parameters(conf)
        
    def test(self):
        try:
            logging.info("Get restrict ipv6 access list via ZD CLI")
            cli_guest_access_info = lib.zdcli.guest_access.get_restricted_access(self.zdcli)
            
            if cli_guest_access_info.get('restricted_ipv6_access'):
                cli_get_ipv6_access_dict = cli_guest_access_info['restricted_ipv6_access']['rules']
                #Remove default guest ipv6 access from cli get. Default order is 1.    
                for order_id in cli_get_ipv6_access_dict.keys():
                    if int(order_id) < 2:
                        cli_get_ipv6_access_dict.pop(order_id)
                self.cli_get_ipv6_access_dict = cli_get_ipv6_access_dict
            else:
                self.errmsg = "Don't get restricted ipv6 access list"
            
        except Exception, ex:
            self.errmsg = ex.message
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Get guest restricted ipv6 access list via ZD CLI successfully"        
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']

        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrier_bag(self):
        self.carrierbag['cli_restricted_ipv6_access_dict'] = self.cli_get_ipv6_access_dict