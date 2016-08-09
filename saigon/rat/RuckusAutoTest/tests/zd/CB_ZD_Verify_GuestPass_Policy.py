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
        
       
Create on 2011-07-11
@author: jluh@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Verify_GuestPass_Policy(Test):
    '''
    verify the guestaccess policy on zd
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
    def test(self):
        try:
            res = self._verify_guestpass_policy_setting()
            self.passmsg = "Confirm the guestaccess policy which is expected."
            logging.info(self.passmsg)
            return self.returnResult('PASS', self.passmsg)
        except Exception, ex:
            return self.returnResult('FAIL', ex)
            
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.guestpass_policy_cfg = dict()
        self.guestpass_policy_cfg.update(conf)   
                
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('existed_guestpass_policy') and self.carrierbag['existed_guestpass_policy']:
            self.guestpass_policy_cfg.update(self.carrierbag['existed_guestpass_policy'])
    
    
    def _update_carrier_bag(self):
        pass
    
    
    def _verify_guestpass_policy_setting(self):
        active_guestpass_policy_cfg = self.zd.get_guestpass_policy()
        res = self._verify_guestpass_policy_dict(self.guestpass_policy_cfg,
                                                 active_guestpass_policy_cfg)
        if not res:
            return False
        
        return res
    
    
    def _verify_guestpass_policy_dict(self, target = dict(), source = dict()):
        for key, value in source.items():
            if target[key] != value :
                self.errmsg = 'Value can not match against key = %s' % key
                return False
        
        return True
    
