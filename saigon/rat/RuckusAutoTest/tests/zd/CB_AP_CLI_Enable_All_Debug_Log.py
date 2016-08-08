# Copyright (C) 2013 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Mar 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'RuckusAP'
   Test parameters:
       - 
        
   Test procedure:
    1. Config:
        - initialize test parameters
    2. Test:
        - Go to shell to enable the debug log
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: service is working as expectation. 
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_AP_CLI_Enable_All_Debug_Log(Test):
    required_components = ['LinuxPC']
    parameters_description = {}
    
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        self._enable_all_debug_log()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)        
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {}        
        self.conf.update(conf)
        
        self.ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
                        
        self.errmsg = ''
        self.passmsg = ''
    
    def _enable_all_debug_log(self):
        logging.info('Enable all debug log on AP')
        try:
            lib.apcli.shell.enable_all_debug_log(self.ap)
            self.passmsg = 'Enable all debug log on AP successfully'
        except Exception, e:
            self.errmsg = 'Failed to enable all debug log on AP: %s' % e.message
