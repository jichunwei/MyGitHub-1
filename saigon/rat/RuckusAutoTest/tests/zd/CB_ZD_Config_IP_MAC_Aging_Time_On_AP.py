# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: The case is for configuring station IP_MAC aging time on active AP.
   @author: Sean Chen
   @contact: sean.chen@ruckuswireless.com
   @since: Dec 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on active AP and Zone Director;
   2. Active AP object has been put into carrierbag.
   
   Required components: 'AP'
   Test parameters:
        - ap_tag: active AP tag, created active AP object can be obtained from carrierbag with ap_tag
        - bridge: bridge interface, different bridge with different aging time
        - age_time: the aging time being set to the station IP_MAC info entry 
        
   Test procedure:
    1. Config:
        - Initialize test parameters, and get active AP component.         
    2. Test:
        - Configure station IP_MAC aging time on active AP.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If station IP_MAC aging time can be set without any error
            FAIL: If any error happens during the operation

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging

from RuckusAutoTest.models import Test

class CB_ZD_Config_IP_MAC_Aging_Time_On_AP(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._set_sta_ip_mac_age_time_on_ap()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = 'Set station IP and MAC info aging time on active AP successfully'
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'ap_tag': 'ap1', 'bridge': 'br0', 'age_time': '8'}
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']

    def _set_sta_ip_mac_age_time_on_ap(self):
        logging.info('Configure station IP and MAC info aging time on active AP')
        try:
            self.active_ap.set_sta_ip_mac_age_time(bridge = self.conf['bridge'], 
                                                   age_time = self.conf['age_time'])
        except Exception, ex:
            self.errmsg = ex.message
