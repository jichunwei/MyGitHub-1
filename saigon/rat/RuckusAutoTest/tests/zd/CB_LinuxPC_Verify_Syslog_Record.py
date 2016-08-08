# Copyright (C) 2013 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Mar 2013

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

class CB_LinuxPC_Verify_Syslog_Record(Test):
    required_components = ['LinuxPC']
    parameters_description = {}
    
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        self._verify_syslog_record()
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)        
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'expected_info': [],
                     'expected_log_file_paths': [],
                     'is_empty': False,
                     'is_optional': False,
                     'ap_tag': ''
                     }        
        self.conf.update(conf)
        
        self.server = self.testbed.components['LinuxServer']
        if self.carrierbag.get('logged_events'):
            self.conf['expected_info'].extend(self.carrierbag['logged_events'])
        if self.conf.get('ap_tag'):
            ap_ip = self.carrierbag[self.conf['ap_tag']]['ap_ins'].ip_addr
            self.conf['expected_info'].append(ap_ip)
        else:
            zd_ip = self.testbed.components['ZoneDirector'].ip_addr
            self.conf['expected_info'].append(zd_ip)
            
        if not self.conf['expected_log_file_paths']:
            self.conf['expected_log_file_paths'].append('/var/log/messages')
                        
        self.errmsg = ''
        self.passmsg = ''
    
    def _verify_syslog_messages_from(self, file_path):
        logmsg = []
        if not self.conf['expected_info']:
            logmsg = self.server.get_syslog_messages(file_path=file_path)
        for msg in self.conf['expected_info']:
            logmsg.extend(self.server.get_syslog_messages_from(msg, file_path=file_path))
        logging.info('[LinuxPC] Get and verify log record on %s' % file_path)
        logging.debug('Result: %s' % logmsg)
        
        if not logmsg and self.conf['is_empty']:
            msg = ' There is not any log in %s as expected.' % file_path
            logging.debug(msg)
            self.passmsg += msg
        elif not logmsg and not self.conf['is_empty']:
            if not self.conf['is_optional']:
                msg = ' The log for %s is not record in %s as expected.' % (self.conf['expected_info'], 
                                                                        file_path)
                logging.debug(msg)
                self.errmsg += msg
            else:
                msg = ' [Optional] There is no log in %s' % file_path
                logging.debug(msg)
                self.passmsg += msg
        elif logmsg and self.conf['is_empty']:
            msg = ' There are log for %s in %s instead of empty' % (self.conf['expected_info'], 
                                                                    file_path)
            
            logging.debug(msg)
            self.errmsg += msg
        elif logmsg and not self.conf['is_empty']:
            if not self.conf['is_optional']:
                msg = ' There are log for %s in %s as expected' % (self.conf['expected_info'], 
                                                               file_path)
                logging.debug(msg)
                self.passmsg += msg
        
        return logmsg            
    
    def _verify_syslog_record(self):
        for file_path in self.conf['expected_log_file_paths']:
            self._verify_syslog_messages_from(file_path)
        
        if self.errmsg:
            self.errmsg = '[LinuxPC] %s' % self.errmsg
            return
        
        self.passmsg = '[LinuxPC] %s' % self.passmsg