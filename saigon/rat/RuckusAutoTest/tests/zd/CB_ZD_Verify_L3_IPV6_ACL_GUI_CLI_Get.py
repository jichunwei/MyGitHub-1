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
        - Compare the data between GUI get and CLI get          
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If data are same between get and set 
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import l3_acl

class CB_ZD_Verify_L3_IPV6_ACL_GUI_CLI_Get(Test):
    required_components = []
    parameters_description = {}
    
    def config(self, conf):
        self._cfg_init_test_params(conf)
        
    def test(self):
        try:
            logging.info("Verify GUI get and CLI get values for L3 IPV6 ACL")
            logging.debug("GUI get: %s, CLI get: %s" % (self.gui_get_acl_cfg, self.cli_get_acl_cfg))
            self.errmsg = l3_acl._verify_l3acl_ipv6_gui_cli_get(self.gui_get_acl_cfg, self.cli_get_acl_cfg)
        except Exception, ex:
            self.errmsg = 'GUI get and CLI get failed:%s' % (ex.message)
        
        if self.errmsg:
            return self.returnResult("FAIL",self.errmsg)
        else:   
            pass_msg = 'GUI get and CLI get data are same'
            return self.returnResult('PASS', pass_msg)
        
    def cleanup(self):
        pass
        
    def _cfg_init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
                
        self.gui_get_acl_cfg = self.carrierbag['existing_l3_ipv6_acls']
        self.cli_get_acl_cfg = self.carrierbag['existing_cli_l3_ipv6_acls']
            
        self.errmsg = ''
        
        
    