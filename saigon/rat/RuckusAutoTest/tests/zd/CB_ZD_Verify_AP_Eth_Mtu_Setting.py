# Copyright (C) 2013 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: The case is for verifying AP eth port MTU configuration.
   @author: Sean Chen
   @contact: sean.chen@ruckuswireless.com
   @since: Mar 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on active AP and Zone Director;
   2. Active AP object has been put into carrierbag.
   
   Required components: 'AP'
   Test parameters:
        - ap_tag: active AP tag, created active AP object can be obtained from carrierbag with ap_tag
        - eth_interface: ethernet interface on AP
        - mtu: the value to check
        - retrieve_mtu: tag for using existing MTU for checking or not
        - expect_status: expect the value same with specific one or not
        
   Test procedure:
    1. Config:
        - Initialize test parameters, and get active AP component.         
    2. Test:
        - Check AP eth port MTU.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If AP eth port MTU is same with expected value
            FAIL: If any error happens or the MTU differs from expected value

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging
import random

from RuckusAutoTest.models import Test

class CB_ZD_Verify_AP_Eth_Mtu_Setting(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._verify_eth_mtu_on_ap()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = "Verify eth port MTU on active AP successfully"
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'ap_tag': 'ap1', 
                     'eth_interface': ['eth0', 'eth1'], 
                     'mtu': 1500,
                     'retrieve_mtu': False,
                     'expect_status': True
                     }
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.current_mtu = self.carrierbag.get('current_mtu')

    def _verify_eth_mtu_on_ap(self):
        logging.info('Verify eth port MTU on active AP')
        try:
            if self.conf['retrieve_mtu']:
                if not self.current_mtu:
                    self.errmsg = 'Need to retrieve MTU but there is no existing value'
                    return
                else:
                    self.conf['mtu'] = self.current_mtu
            
            check_fail_inf = []
            check_ok_inf = []
            for eth_inf in self.conf['eth_interface']:
                res = self.active_ap.verify_eth_mtu(eth_interface = eth_inf, mtu = self.conf['mtu'])
                if not res:
                    check_fail_inf.append(eth_inf)
                else:
                    check_ok_inf.append(eth_inf)
            if self.conf['expect_status']:
                if len(check_fail_inf):
                    self.errmsg = "The MTU differ from %s at port" % self.conf['mtu']
                    for inf in check_fail_inf:
                        self.errmsg += "[%s]" % inf
                    return
            else:
                if len(check_ok_inf):
                    self.errmsg = "The MTU should not be %s  at port" % self.conf['mtu']
                    for inf in check_ok_inf:
                        self.errmsg += "[%s]" % inf
                    return
                    
        except Exception, ex:
            self.errmsg = ex.message
        