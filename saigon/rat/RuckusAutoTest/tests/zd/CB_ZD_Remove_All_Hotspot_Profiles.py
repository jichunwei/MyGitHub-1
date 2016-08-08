# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

'''
Description:

   Prerequisite (Assumptions about the state of the testbed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'ZoneDirector', 'RuckusAP'
   Test parameters: 
   Result type: PASS/FAIL
   Results: PASS:
            FAIL:  

   Messages: If FAIL the test script returns a message related to the criteria that is not satisfied

   Test procedure:
   1. Config:
       - 
   2. Test:
       -            
   3. Cleanup:
       - 
    How it was tested:
        
       
Create on Dec 8, 2011
@author: cherry.cheng@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import hotspot_services_zd as hotspot

class CB_ZD_Remove_All_Hotspot_Profiles(Test):
    '''
    create the guest restricted subnet access on zd
    '''
    required_components = ['ZoneDirector']
    parameter_description = {}
    
    def config(self, conf):
        self._init_test_params(conf)
        
    def test(self):
        self._remove_all_hotspot_profiles()
                
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        else:
            self.passmsg = "Remove all hotspot profiles successfully."
            logging.info(self.passmsg)
            self._update_carrier_bag()
            return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    
    def _update_carrier_bag(self):
        pass     
    
    def _remove_all_hotspot_profiles(self):
        try:
            hotspot.remove_all_profiles(self.zd)
        except Exception, ex:
            self.errmsg = 'Remove all hotspot profiles failed: %s' % ex.message