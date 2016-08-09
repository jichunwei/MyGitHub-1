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
        - Configure syslog server on ZD WebUI
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

class CB_ZD_Config_Syslog(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        if self.conf['cleanup']:
            self._disable_syslog_server()
        else:
            self._setting_syslog_server()
        
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult('FAIL', self.errmsg)
        
        logging.debug(self.passmsg)
        return self.returnResult('PASS', self.passmsg)        
    
    def cleanup(self):
        pass

    def _init_test_params(self, conf):
        self.conf = {'server_ip': '192.168.0.252',
                     'log_level': '',
                     'cleanup': False
                     }
        
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
                        
        self.errmsg = ''
        self.passmsg = ''
        
    def _update_carrierbag(self):
        pass
    
    def _setting_syslog_server(self):
        try:
            self.zd.cfg_syslog_server(checked = True, ip_addr = self.conf['server_ip'], log_level = self.conf['log_level'])
            passmsg = 'Configure syslog[server_ip=%s, log_level=%s] on ZD WebUI successfully' 
            self.passmsg=  passmsg % (self.conf['server_ip'], self.conf['log_level'])
        except Exception, e:
            self.errmsg = 'Fail to enable syslog server option on Zone Director: %s' % e.message       
    
    def _disable_syslog_server(self):
        try:
            self.zd.cfg_syslog_server(checked = False)
            self.passmsg =  'Cleanup the syslog server configuration on ZD WebUI successfully'
        except Exception, e:
            self.errmsg = 'Fail to disable syslog server option on Zone Director: %s' % e.message