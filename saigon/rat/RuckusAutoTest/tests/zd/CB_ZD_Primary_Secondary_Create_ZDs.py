# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: April 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'ZoneDirectorCLI'
   Test parameters:
       - 'invalid_primary_zd_ip_list': "Invalid primary zd ip address values",
       - 'invalid_secondary_zd_ip_list': "Invalid secondary zd ip address values",
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Configure limited ZD discovery with valid values.
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: Error message is correct.

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test

class CB_ZD_Primary_Secondary_Create_ZDs(Test):
    required_components = []
    parameters_description = {'zd_tag_list': 'Zd tag list'}
    
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        try:
            logging.info("Get ZD components from testbed components and put them in carrier bag")
            for zd_tag in self.zd_tag_list:
                if self.testbed.components.has_key(zd_tag):
                    self.carrierbag[zd_tag] = self.testbed.components[zd_tag]
                else:
                    raise Exception("No components and configuration in test bed.")
                    
        except Exception, e:
            self.errmsg = "Find ZD components failed: [%s]" % e.message
            
        if self.errmsg:
            logging.debug(self.errmsg)
            return self.returnResult("FAIL", self.errmsg)
        else:
            self._update_carrier_bag()
            self.passmsg = "Find and Create ZD components successfully"
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'zd_tag_list': ['ZoneDirector', 'ZoneDirectorCLI'],
                     }
        
        self.conf.update(conf)
        
        self.zd_tag_list = self.conf['zd_tag_list']
        
        self.errmsg = ''
        self.passmsg = ''