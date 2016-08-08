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
        
       
Create on Jul 29, 2011
@author: jluh@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Set_GuestAccess_Policy(Test):
    '''
    create the guest policy on zd
    '''
    required_components = []
    parameter_description = {}
    
    def config(self, conf):
        self._init_test_params(conf)
    
        
    def test(self):
        self._create_guest_access_policy()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        self.passmsg = "Create the guest access policy successufully."
        logging.info(self.passmsg)
        self._update_carrier_bag()
        return self.returnResult("PASS", self.passmsg)
        
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.guestaccess_cfg = dict(use_guestpass_auth = True,
                                    enable_share_guestpass = False,
                                    use_tou = True,
                                    redirect_url = 'http://www.example.net/'
                                    )
        self.guestaccess_cfg.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_guestaccess_policy'] = self.guestaccess_cfg
        
    
    def _create_guest_access_policy(self):
        try:
            self.zd.set_guestaccess_policy(**self.guestaccess_cfg)
        except Exception, ex:
            self.errmsg = '[Guest Access Policy creating failed] %s' % ex.message
            logging.debug(self.errmsg)
            
    
    
        
    
        

        