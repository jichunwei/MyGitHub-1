# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: An Nguyen
   @contact: an.nguyen@ruckuswireless.com
   @since: Jul 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'ZoneDirector', 'ZoneDirectorCLI', 'RuckusAP'
   Test parameters:
       - 
        
   Test procedure:
    1. Config:
        - initialize test parameters
    2. Test:
        - Getting the syslog setting
        - Verify if the expected info
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: service is working as expectation. 
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import re
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_DHCP_Service_Log(Test):
    required_components = ['ZoneDirector', 'ZoneDirectorCLI', 'RuckusAP']
    parameters_description = {}
    
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        self._verify_expected_log()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)        
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'zd_tag': '',
                     'pattern_name': '',
                     'expected_key': '',
                     'waiting_time': 120,
                     }        
        self.conf.update(conf)
        
        if self.conf['zd_tag']:
            self.zd = self.carrierbag.get(self.conf['zd_tag'], None)
        if not self.zd:
            self.zd = self.testbed.components['ZoneDirector']
        
        self._define_expected_log()
        if self.conf['pattern_name'].lower() == 'rogue_dhcp_detect':
            self._disable_then_enable_rouge_dhcp_detect_option()
        
        self.errmsg = ''
        self.passmsg = ''

    def _define_expected_log(self):
        pattern_dict = {'enable_dhcp_server': 'DHCP server enabled with IP range from \[.+\] to \[.+\]',
                        'rogue_dhcp_detect': 'Rogue DHCP server detected on \[.+\]'}
        self.expected_pattern = pattern_dict.get(self.conf['pattern_name'].lower(), None)
        if not self.expected_pattern:
            raise Exception('Does not support to verify the log for "%s"' % self.conf['pattern_name'])
    
    def _disable_then_enable_rouge_dhcp_detect_option(self):
        from RuckusAutoTest.components.lib.zd import wips_zd as wips
        wips.disable_rogue_dhcp_server_detection(self.zd)
        logging.info('disable dhcp server dection successfully')
        time.sleep(2)
        wips.enable_rogue_dhcp_server_detection(self.zd)
        logging.info('enable dhcp server dection successfully')
        time.sleep(2)
        
    def _verify_expected_log(self):
        logging.info("[PAUSE] %s sec" % self.conf['waiting_time'])
        time.sleep(self.conf['waiting_time'])
        all_logs = lib.zd.zd_log.get_events(self.zd)
        catched_logs = []
        for log in all_logs:
            if not re.match(self.expected_pattern, log['activities']):
                continue
            if self.conf['expected_key'] in log['activities']:
                catched_logs.append(log)
        
        if not catched_logs:
            msg = 'Can not find any "%s" log with the key "%s"' 
            self.errmsg =  msg % (self.conf['pattern_name'], self.conf['expected_key'])
            logging.info(self.errmsg)
            return
        
        msg = 'The expected log for "%s" with key "%s": %s' 
        msg = msg % (self.conf['pattern_name'], self.conf['expected_key'], catched_logs)
        logging.info(msg)
        msg = 'The expected log for "%s" with the key "%s" are shown as expected'
        self.passmsg = msg % (self.conf['pattern_name'], self.conf['expected_key'])
        logging.info(self.passmsg)