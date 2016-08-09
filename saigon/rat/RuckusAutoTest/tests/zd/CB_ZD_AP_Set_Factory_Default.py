# Copyright (C) 2011 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: cherry.cheng@ruckuswireless.com
   @since: April 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the Station

   Required components: 'AccessPoint'
   Test parameters:
       - ap_tag: access point tag.
        
   Test procedure:
    1. Config:
        - initialize test parameters         
    2. Test:
        - Set ap to factory default  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: AP is set to factory default successfully.
                FAIL: If any item is incorrect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import logging

from RuckusAutoTest.models import Test

class CB_ZD_AP_Set_Factory_Default(Test):
    required_components = ['AccessPoint']
    parameters_description = {'ap_tag': 'Access point tag'}

    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()        
    
    def test(self):
        for active_ap in self.active_ap_list:
            ap_mac = active_ap.get_base_mac()
            logging.info("Set AP %s to factory default" % ap_mac)
            active_ap.set_factory()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = {'ap_tag': ''}        
        self.conf.update(conf)
        
        ap_tag = self.conf['ap_tag']
        self.active_ap_list = []
        if ap_tag:
            if type(ap_tag) != list:
                ap_tag_list = [ap_tag]
            else:
                ap_tag_list = ap_tag
                
            for aptag in ap_tag_list:
                self.active_ap_list.append(self.carrierbag[aptag]['ap_ins'])
        else:
            #If no ap_tag is specified, will set all ap as specified values.
            self.active_ap_list = self.testbed.components['AP']
       
        self.errmsg = ''
        self.passmsg = ''
        
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass