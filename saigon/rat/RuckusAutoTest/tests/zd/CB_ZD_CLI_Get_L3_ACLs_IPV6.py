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
        - Get all l3 ipv6 acls list via ZD CLI.
                
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Get l3 ipv6 acls6 successfully
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import l3_acl

class CB_ZD_CLI_Get_L3_ACLs_IPV6(Test):
    required_components = ['ZoneDirectorCLI']
    parameter_description = {}

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        logging.info("Get L3/4/IPv6 address Access Control via CLI")
        self.current_l3_acls_ipv6 = l3_acl.show_l3acl_ipv6_all(self.zdcli)
        
        if self.errmsg:
            return ('FAIL', self.errmsg)
        else:
            self.passmsg = 'Get L3 IPV6 ALCs via CLI successfully'
            self._update_carrier_bag()
            return ('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        args = dict()
        args.update(conf)
        
        self.zdcli = self.testbed.components['ZoneDirectorCLI']
         
        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrier_bag(self):
        self.carrierbag['existing_cli_l3_ipv6_acls'] = self.current_l3_acls_ipv6      
    