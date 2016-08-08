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
        - Compare aaa servers between GUI get and CLI get
                
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Data between gui get and cli get are same
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zdcli import aaa_servers as cas

class CB_ZD_Verify_AAA_Server_GUI_CLI_Get(Test):
    required_components = []
    parameters_description = {}
    
    
    def config(self, conf):
        self._initTestParameters(conf)

    def test(self):
        logging.debug("GUI: %s" % self.gui_get_server_list)
        logging.debug("CLI: %s" % self.cli_get_server_list)
        self._verify_server_gui_cli_get()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = "The servers information are same between GUI get and CLI get"
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
        
    def _initTestParameters(self, conf):
        self.gui_get_server_list = self.carrierbag['zdgui_server_info_list']
        self.cli_get_server_list = self.carrierbag['zdcli_server_info_list']
         
        self.errmsg = ''
        self.passmsg = ''

    def _verify_server_gui_cli_get(self):
        logging.info('Verify the AAA server settings between GUI get and CLI get')
        try:
            err_msg = cas.verify_server_cfg_gui_cli_get(self.gui_get_server_list, self.cli_get_server_list)
            if err_msg:
                self.errmsg = err_msg
        except Exception, ex:
            self.errmsg = ex.message