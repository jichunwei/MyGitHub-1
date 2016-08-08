# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
# Please make sure the following module doc string is accurate since it will be used in report generation.

"""Description:

    Prerequisite (Assumptions about the state of the testbed/DUT):

    Required components:
    Test parameters:
    Result type: PASS/FAIL
    Results: PASS
             FAIL otherwise

    Messages:
        - If PASS,
        - If FAIL, prints out the reason for failure

    Test procedure:
    1. Config:
        -
    2. Test:
        -
    3. Cleanup:
        -

    How is it tested: (to be completed by test code developer)

"""

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_ZD_Create_GuestPass_Policy(Test):
    '''
    create the guestpass policy on zd
    '''
    def config(self, conf):
        self._init_test_params(conf)
        
        
    def test(self):
        passmsg = []
        self.errmsg = self.zd.set_guestpass_policy(**self.guestpass_cfg)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        self.passmsg = "Create the guestpass policy successufully."
        passmsg.append(self.passmsg)
        logging.info(self.passmsg)
        self._update_carrier_bag()
        self.returnResult('PASS', self.passmsg)
        
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        guestpass_cfg = dict(auth_serv = "", 
                             is_first_use_expired = False, 
                             valid_day = '5',
                             )
        guestpass_cfg.update(conf)
        
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_guestpass_policy'] = self.guestpass_cfg
    
    
        
    
        

        