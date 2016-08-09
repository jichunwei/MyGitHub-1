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
        - Remove all events on ZD
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: service is working as expectation. 
            FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging
from RuckusAutoTest.models import Test

class CB_ZD_Remove_All_Events(Test):
    required_components = ['ZoneDirector']
    parameters_description = {}
    
    def config(self,conf):
        self._init_test_params(conf)
    
    def test(self):
        self._remove_all_events_on_zd()        
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
    
    def _remove_all_events_on_zd(self):
        try:
            self.zd.clear_all_events()
            self.passmsg = 'Clear all ZD events/activities successfully'
        except Exception, e:
            self.errmsg = 'Fail to lear all ZD events/activities: %s' % e.message       