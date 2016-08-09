# Copyright (C) 2013 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: The case is for configuring station eth port MTU.
   @author: Sean Chen
   @contact: sean.chen@ruckuswireless.com
   @since: Feb 2013

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on active AP and Zone Director;
   2. Active AP object has been put into carrierbag.
   
   Required components: 'Station'
   Test parameters:
        - sta_tag: station tag, created station object can be obtained from carrierbag with sta_tag
        - mtu: the value to set
        - do_random: tag for using random MTU value or not
        - random_range: the value range among which to make random choice
        - retrieve_sta_mtu: tag for using existing MTU or not
        
   Test procedure:
    1. Config:
        - Initialize test parameters, and get station component.         
    2. Test:
        - Configure station eth port MTU.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If station eth port MTU can be set without any error
            FAIL: If any error happens during the operation

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging
import random

from RuckusAutoTest.models import Test

class CB_ZD_Sta_Eth_Mtu_Setting(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        self._set_eth_mtu_on_sta()
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            self.passmsg = 'Configure eth port MTU to %s on station successfully' % self.conf['mtu']
            self._update_carribag()
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'sta_tag': 'sta1', 
                     'mtu': 1500,
                     'do_random': False,
                     'random_range': (),
                     'retrieve_sta_mtu': False,
                     }
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.station = self.carrierbag[self.conf['sta_tag']]['sta_ins']
        self.current_sta_mtu = self.carrierbag.get('current_sta_mtu')

    def _set_eth_mtu_on_sta(self):
        logging.info('Configure eth port MTU on station')
        try:
            if self.conf['retrieve_sta_mtu']:
                if not self.current_sta_mtu:
                    self.errmsg = 'Need to retrieve station MTU but there is no existing value'
                    return
                else:
                    self.conf['mtu'] = self.current_sta_mtu
            elif self.conf['do_random']:
                self.conf['mtu'] = random.randint(self.conf['random_range'][0], self.conf['random_range'][1])
            self.station.set_eth_mtu(mtu = self.conf['mtu'])
                
        except Exception, ex:
            self.errmsg = ex.message

    def _update_carribag(self):
        self.carrierbag['current_sta_mtu'] = self.conf['mtu']