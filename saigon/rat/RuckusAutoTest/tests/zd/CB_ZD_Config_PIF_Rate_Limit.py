# Copyright (C) 2012 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module docstring is accurate since it will be used in report generation.

"""
   Description: The case is for configuring PIF rate limit on ZD.
   @author: Sean Chen
   @contact: sean.chen@ruckuswireless.com
   @since: Dec 2012

   Prerequisite (Assumptions about the state of the test bed/DUT):
   1. Build under test is loaded on active AP and Zone Director;
   2. Zone Director object has been put into carrierbag.
   
   Required components: 'ZoneDirector'
   Test parameters:
        - check_only: only check the PIF rate limit current configuration without configuring
        - expected_status: PIF rate limit status (on/off) expected to be or to be set
        - expected_rate_limit: PIF rate limit value expected to be or to be set
        - do_random: set PIF rate limit value with a random value or not
        - random_range: the range for the random value
        - expect_config_done: expect the operation to be completed or not
        
   Test procedure:
    1. Config:
        - Initialize test parameters, and get ZD component.         
    2. Test:
        - Configure PIF rate limit on ZD.  
    3. Cleanup:
        - N/A
   
   Result type: PASS/FAIL
   Results: PASS: If the PIF rate limit current configuration is as expected or can be set as expected
            FAIL: If the configuration is unmatched the expected or any error happens during setting

   Messages: If FAIL the test script returns a message related to the criterion that is not satisfied
"""


import logging
import random

from RuckusAutoTest.models import Test

class CB_ZD_Config_PIF_Rate_Limit(Test):

    def config(self, conf):
        self._init_test_parameters(conf)

    def test(self):
        if self.conf['check_only']:
            self._verify_pif_rate_limit_on_zd()
        else:
            self._set_pif_rate_limit_on_zd()
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:
            return self.returnResult('PASS', self.passmsg)

    def cleanup(self):
        pass

    def _init_test_parameters(self, conf):
        self.conf = {'check_only': False, 
                     'expected_status': False,
                     'expected_rate_limit': None,
                     'do_random': False,
                     'random_range': (0, 3000),
                     'expect_config_done': True}
        self.conf.update(conf)
        self._retrieve_carribag()
        self.errmsg = ''
        self.passmsg = ''

    def _retrieve_carribag(self):
        self.zd = self.testbed.components['ZoneDirector']
        
    def _verify_pif_rate_limit_on_zd(self):
        logging.info('Verify PIF rate limit setting on ZD')
        try:
            res = self.zd.verify_pif_rate_limit(expected_status = self.conf['expected_status'],
                                                expected_rate_limit = self.conf['expected_rate_limit'])
            if not res:
                self.errmsg = 'The PIF rate limit setting is not the same as expected'
            else:
                self.passmsg = 'The PIF rate limit setting is same as expected'
                
        except Exception, ex:
            self.errmsg = ex.message
    
    def _set_pif_rate_limit_on_zd(self):
        logging.info('Configure PIF rate limit on ZD')
        try:
            if self.conf['do_random']:
                self.conf['expected_rate_limit'] = random.randint(self.conf['random_range'][0], self.conf['random_range'][1])
                
            res = self.zd.set_pif_rate_limit(expected_status = self.conf['expected_status'],
                                             expected_rate_limit = self.conf['expected_rate_limit'])
            
            if self.conf['expect_config_done']:
                if not res:
                    self.errmsg = 'The PIF rate limit cannot be set as expected'
                else:
                    self.passmsg = 'The PIF rate limit can be set successfully'
            else:
                if res:
                    self.errmsg = 'The PIF rate limit can be set with wrong value, incorrect behavior'
                else:
                    self.passmsg = 'The PIF rate limit cannot be set with wrong value, correct behavior'
            
        except Exception, ex:
            self.errmsg = ex.message
    