# Copyright (C) 2013 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: The case is for configuring AP eth port MTU.
   @author: Sean Chen
   @contact: sean.chen@ruckuswireless.com
   @since: Feb 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on active AP and Zone Director;
   2. Active AP object has been put into carrierbag.
   
   Required components: 'AP'
   Test parameters:
        - ap_tag: active AP tag, created active AP object can be obtained from carrierbag with ap_tag
        - eth_interface: ethernet interface on AP
        - mtu: the value to set
        - over_data_size: increment bytes needed to add to specified MTU
        - do_random: tag for using random MTU value or not
        - random_range: the value range among which to make random choice
        - retrieve_mtu: tag for using existing MTU or not
        - expect_status: expect the value can be set or not
        
   Test procedure:
    1. Config:
        - Initialize test parameters, and get active AP component.         
    2. Test:
        - Configure AP eth port MTU.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If AP eth port MTU can be set without any error
            FAIL: If any error happens during the operation

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging
import random

from RuckusAutoTest.models import Test

class CB_ZD_AP_Eth_Mtu_Setting(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._set_eth_mtu_on_ap()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'ap_tag': 'ap1', 
                     'eth_interface': ['eth0', 'eth1'], 
                     'mtu': 1500,
                     'over_data_size': 0,
                     'do_random': False,
                     'random_range': (),
                     'retrieve_mtu': False,
                     'retrieve_sta_mtu': False,
                     'expect_status': True
                     }
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.active_ap = self.carrierbag[self.conf['ap_tag']]['ap_ins']
        self.current_mtu = self.carrierbag.get('current_mtu')
        self.current_sta_mtu = self.carrierbag.get('current_sta_mtu')

    def _set_eth_mtu_on_ap(self):
        logging.info('Configure eth port MTU on active AP')
        try:
            if self.conf['retrieve_mtu']:
                if not self.current_mtu:
                    self.errmsg = 'Need to retrieve MTU but there is no existing value'
                    return
                else:
                    self.conf['mtu'] = self.current_mtu
            elif self.conf['retrieve_sta_mtu']:
                if not self.current_sta_mtu:
                    self.errmsg = 'Need to retrieve station MTU but there is no existing value'
                    return
                else:
                    self.conf['mtu'] = self.current_sta_mtu
            elif self.conf['do_random']:
                self.conf['mtu'] = random.randint(self.conf['random_range'][0], self.conf['random_range'][1])
            self.conf['mtu'] += self.conf['over_data_size']
            
            set_fail_inf = []
            set_ok_inf = []
            for eth_inf in self.conf['eth_interface']:
                res = self.active_ap.set_eth_mtu(eth_interface = eth_inf, mtu = self.conf['mtu'])
                if not res:
                    set_fail_inf.append(eth_inf)
                else:
                    set_ok_inf.append(eth_inf)
            if self.conf['expect_status']:
                if len(set_fail_inf):
                    self.errmsg = "Expect can set MTU to %s but set failed at port" % self.conf['mtu']
                    for inf in set_fail_inf:
                        self.errmsg += "[%s]" % inf
                    return
                else:
                    # Reboot AP to make the setting take effect.
                    self.active_ap.reboot()
                    self.passmsg = "Configure eth port MTU to %s on active AP successfully" % self.conf['mtu']
                    self._update_carribag()
            else:
                if len(set_ok_inf):
                    self.errmsg = "Expect cannot set MTU to %s but set ok at port" % self.conf['mtu']
                    for inf in set_ok_inf:
                        self.errmsg += "[%s]" % inf
                    return
                else:
                    self.passmsg = "Correct behavior, cannot set MTU to %s at port" % self.conf['mtu']
                    for inf in set_fail_inf:
                        self.passmsg += "[%s]" % inf
                    
        except Exception, ex:
            self.errmsg = ex.message
        
    def _update_carribag(self):
        self.carrierbag['current_mtu'] = self.conf['mtu']