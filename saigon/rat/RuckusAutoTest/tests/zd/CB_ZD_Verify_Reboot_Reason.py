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

import re
import types
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_Reboot_Reason(Test):
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
        return self.returnResult('PASS', self.passmsg)        
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'ap_tag': '',
                     #'expected_reason': '',
                    }        
        self.conf.update(conf)
        self.reason = self.conf.get('expected_reason',[])
        self.expected_reasons = []
        if type(self.reason) is types.StringType:
            self.expected_reasons.append(self.reason)
        elif type(self.reason) is types.ListType:
            self.expected_reasons = self.reason
        
        self.zd = self.testbed.components['ZoneDirector']
        
        if self.conf['ap_tag']:
            ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
            self.ap_mac = ap.base_mac_addr
        else:
            self.ap_mac = 'No AP TAG is defined'
            
        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrierbag(self, event):
        if not self.carrierbag.has_key('logged_events'):
            self.carrierbag['logged_events'] = []
        self.carrierbag['logged_events'].append(event)
    
    def _verify_syslog_messages(self):
        #ap_application_reboot = 'AP\[%s\] joins .* last reboot reason \[application reboot\]' % self.ap_mac
        #AP[c0:8a:de:1d:d6:90] joins with uptime [49] s and last disconnected reason [AP Restart : application reboot]
        #    AP[c0:8a:de:1d:d6:90] joins with uptime [48] s and last disconnected reason [AP Restart : user reboot]
        #AP[c0:8a:de:1d:d6:90] joins with uptime [255] s and last disconnected reason [Heartbeat Loss]
        #@author: chen.tao 2014-01-08 to fix behavior change ZF-6176
        #@author: li.pingping @bug: ZF-8392 @since: 2014-7-10
        ap_application_reboot = 'AP\[%s\] joins .* last disconnected reason \[AP Restart : application reboot\]' % self.ap_mac
        #ap_application_reboot = 'AP\[%s\] joins .* last reboot reason \[application reboot\]' % self.ap_mac
        ap_user_reboot = 'AP\[%s\] joins .* last disconnected reason \[AP Restart : user reboot\]' % self.ap_mac
        #ap_user_reboot = 'AP\[%s\] joins .* last reboot reason \[user reboot\]' % self.ap_mac
        zd_warm_reboot = 'System warm restarted'
        ap_heartbeat_loss = 'AP\[%s\] joins .* last disconnected reason \[Heartbeat Loss\]' % self.ap_mac
        #ap_heartbeat_loss = 'AP\[%s\] joins .* last reboot reason \[user reboot\]' % self.ap_mac
        #@author: chen.tao 2014-01-08 to fix behavior change ZF-6176
        #2013/05/06  22:31:24    ZD warm restart    Medium    System warm restarted with [user reboot]
        re_log_events = {'ap application reboot': ap_application_reboot,
                         'ap user reboot': ap_user_reboot,
                         'zd warm reboot': zd_warm_reboot,
                         'ap heartbeat loss': ap_heartbeat_loss}
        
        all_events = lib.zd.zd_log.get_events(self.zd)
        for event in all_events:
            for reason in self.expected_reasons:
                if re.match(re_log_events[reason], event['activities']):
                    self.passmsg = 'The expected event is found %s' % event
                    self._update_carrierbag(event['activities'])
                    return
        
        
        for reason in self.expected_reasons:
            self.errmsg += ('Can not find the expected event[%s]'  % re_log_events[reason])