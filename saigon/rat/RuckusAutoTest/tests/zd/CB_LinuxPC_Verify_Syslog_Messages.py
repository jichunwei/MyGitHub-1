# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Nov 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'Linux PC'
   Test parameters:
       - 
        
   Test procedure:
    1. Config:
        - initialize test parameters
    2. Test:
        - Getting the syslog messages
        - Verify if the expected messages
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: service is working as expectation. 
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
from RuckusAutoTest.models import Test

class CB_LinuxPC_Verify_Syslog_Messages(Test):
    required_components = ['LinuxPC']
    parameters_description = {}
    
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        self._verify_syslog_messages()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        logging.debug(self.passmsg)
        self._update_carrierbag()
        return self.returnResult('PASS', self.passmsg)        
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'expected_msgs': [],
                     'clear_carrier_bag': True,
                     }        
        self.conf.update(conf)
        
        self.server = self.testbed.components['LinuxServer']
        if self.carrierbag.get('logged_events'):
            self.conf['expected_msgs'].extend(self.carrierbag['logged_events'])
                        
        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrierbag(self):
        if self.conf['clear_carrier_bag']:
            self.carrierbag['logged_events'] = []
    
    def _verify_syslog_messages(self):
        errlog = [] 
        #@author: Anzuo, ZF-6174
        if not self.conf['expected_msgs']:
            self.errmsg = "There is no expected msg found in conf, self.conf['expected_msgs'] = %s" % self.conf['expected_msgs']
            return 
        
        for msg in self.conf['expected_msgs']:
            logmsg = self.server.get_syslog_messages_from(msg)
            if not logmsg:
                errlog.append(msg)
        
        if errlog:
            self.errmsg = 'The following message %s are not found on syslog server' % errlog
            return
        self.passmsg = 'All message %s are logged to the syslog server' % self.conf['expected_msgs']
                