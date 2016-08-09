# Copyright (C) 2010 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: 
   @author: Cherry Cheng
   @contact: Cherry.cheng@ruckuswireless.com
   @since: Aug 2011

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. N/A

   Required components: 'L3Switch'
   Test parameters:
        N/A 
        
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Clear mac address table in L3 Switch         
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS: If mac address table is clear.
   
   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging

from RuckusAutoTest.models import Test

class CB_Switch_Clear_Mac_Table(Test):
    required_components = ['L3Switch']
    parameter_description = {}

    
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()

    def test(self):
        self._clear_mac_table()
        
        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrier_bag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):        
        self.errmsg = ''
        self.passmsg = ''
        
        self.switch = self.testbed.components["L3Switch"]

    def _clear_mac_table(self):
        
        logging.info('Clear mac table in Swtich')
        try:
            self.switch.clear_mac_table()            
            self.passmsg = 'Clear mac table in switch successfully.'
            
        except Exception, ex:
            self.errmsg = ex.message   
    