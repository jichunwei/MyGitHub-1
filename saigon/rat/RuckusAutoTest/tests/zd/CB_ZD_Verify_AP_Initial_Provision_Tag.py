"""
   Description: 
   @author: Kevin Tan
   @contact: kevin.tann@ruckuswireless.com
   @since: October 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on the AP and Zone Director

   Required components: 'Station', 'RuckusAP', 'ZoneDirector'
   Test parameters:
   
   Test procedure:
    1. Config:
        -         
    2. Test:
        - Verify if get or set AP IPT(Initial Provision Tag in AP CLI) successfully or not. 
    3. Cleanup:
        -
   
   Result type: PASS/FAIL
   Results: PASS: get or set AP IPT correctly
            FAIL: get or set AP IPT incorrectly

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""

import time
import logging
from pprint import pformat

from RuckusAutoTest.models import Test

class CB_ZD_Verify_AP_Initial_Provision_Tag(Test):
    def config(self, conf):
        self._init_test_parameter(conf)

    def test(self):
        op = self.conf['operation']
        
        if op == 'get':
            ipt = self.active_ap.get_ipt_option()
            if ipt != self.conf['ipt']:
                self.errmsg = 'get IPT[%s] invalid, should be %s' % (ipt, self.conf['ipt'])
        elif op == 'set':
            try:
                self.active_ap.set_ipt_option(self.conf['ipt'])
            except:
                self.errmsg = 'Exception when setting IPT[%s] to active AP failed' % self.conf['ipt']
        else:
            self.errmsg = 'operation[%s] invalid, should be get or set' % op

        if self.errmsg: 
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _init_test_parameter(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.apmac = self.active_ap.base_mac_addr
        self.passmsg = ''
        self.errmsg = ''
