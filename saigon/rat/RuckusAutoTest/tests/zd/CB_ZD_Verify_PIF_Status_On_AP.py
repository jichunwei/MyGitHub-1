# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: The case is for verifying PIF status on active AP.
   @author: Sean Chen
   @contact: sean.chen@ruckuswireless.com
   @since: Dec 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on active AP and Zone Director;
   2. Active AP object has been put into carrierbag.
   
   Required components: 'AP'
   Test parameters:
        - ap_tag: active AP tag, created active AP object can be obtained from carrierbag with ap_tag
        - bridge: bridge interface, different bridge with different PIF information
        - expected_status: the PIF status expected to be
        
   Test procedure:
    1. Config:
        - Initialize test parameters, and get active AP component.         
    2. Test:
        - Verify PIF status on active AP is same as expect.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If PIF status is same as expect
            FAIL: If PIF status is different as expect

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging

from RuckusAutoTest.models import Test

class CB_ZD_Verify_PIF_Status_On_AP(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._verify_pif_status_on_ap()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self._update_carrierbag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'ap_tag': 'ap1', 'bridge':'br0', 'expected_status': 'no'}
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        
    def _verify_pif_status_on_ap(self):
        logging.info('Verify PIF status on active AP')
        br_info = self.active_ap.get_bridge_setting(bridge = self.conf['bridge'])
        if self.conf['expected_status'].lower() != br_info[0]['PIF'].lower():
            self.errmsg = 'The PIF status on active AP is %s instead of %s' % (br_info[0]['PIF'], self.conf['expected_status'])
            return
        else:
            self.passmsg = 'The PIF status on active AP is correct'
        
    def _update_carrierbag(self):
        pass
