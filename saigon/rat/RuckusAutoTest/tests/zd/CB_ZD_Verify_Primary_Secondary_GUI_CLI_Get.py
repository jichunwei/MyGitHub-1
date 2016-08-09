# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: April 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: N/A
   Test parameters:       
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Verify ZD discovery confgiuration between GUI set and get.
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: The settings are same.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import config_ap_policy as lib

class CB_ZD_Verify_Primary_Secondary_GUI_CLI_Get(Test):
    required_components = []
    parameters_description = {}
    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            logging.info("Verify limited ZD discovery settings between GUI get and CLI get")
            self.errmsg = lib.verify_limited_zd_discovery(self.gui_get_zd_discoverty_cfg, self.cli_get_zd_discoverty_cfg)            
        except Exception, e:
            self.errmsg = "Fail to verify limited ZD discovery: %s" % e.message
        
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Limited ZD discovery setting are same between GUI get and CLI get"            
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        
        self.conf.update(conf)
        self.gui_get_zd_discoverty_cfg = self.carrierbag['gui_zd_discovery_cfg']
        self.cli_get_zd_discoverty_cfg = self.carrierbag['cli_zd_discovery_cfg']
             
        self.errmsg = ''
        self.passmsg = ''