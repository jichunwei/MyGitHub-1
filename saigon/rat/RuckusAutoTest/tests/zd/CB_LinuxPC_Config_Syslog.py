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
        - Setting the expected option of syslog-ng server on Linux PC
        - Verify if the service is running
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: service is working as expectation. 
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
from RuckusAutoTest.models import Test

class CB_LinuxPC_Config_Syslog(Test):
    required_components = ['LinuxPC']
    parameters_description = {}
    
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        if self.conf['restart_server']: 
            self._restart_syslog_server()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        msg = self.passmsg
               
        if self.conf['clear_log']:
            self._clear_syslog_message()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        msg = msg + '. ' + self.passmsg
        
        logging.debug(msg)
        return self.returnResult('PASS', msg)        
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'restart_server': False,
                     'clear_log': True
                     }
        
        self.conf.update(conf)
        
        self.server = self.testbed.components['LinuxServer']
                        
        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrierbag(self):
        pass
    
    def _restart_syslog_server(self):
        try:
            self.server.restart_syslog()
            self.passmsg = 'Restart the syslog-ng server successfully'
        except Exception, e:
            self.errmsg = 'Failed to restart the syslog-ng server: %s' % e.message
            
    def _clear_syslog_message(self):
        syslog_files = ['/var/log/messages', 
                        '/var/log/local0.log', '/var/log/local7.log',
                        '/var/log/local1.log', '/var/log/local2.log', '/var/log/local3.log',
                        '/var/log/local4.log', '/var/log/local5.log', '/var/log/local6.log',
                        '/var/log/test-emerg.log', '/var/log/test-alert.log',
                        '/var/log/test-crit.log', '/var/log/test-err.log',
                        '/var/log/test-warning.log', '/var/log/test-notice.log',
                        '/var/log/test-info.log', '/var/log/test-debug.log']
        try:
            for file_path in syslog_files:
                self.server.clear_syslog_messages(file_path=file_path)
            self.passmsg = 'Clear all syslog messages successfully'
        except Exception, e:
            self.errmsg = 'Failed to clear all syslog message: %s' % e.message

