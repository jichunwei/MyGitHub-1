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
from RuckusAutoTest.components.lib.zd import guest_access_zd as hlp

class CB_ZD_Create_GuestAccess_Policy(Test):
    '''
    create the guest policy on zd
    '''
    def config(self, conf):
        self._init_test_params(conf)
        
        
    def test(self):
        passmsg = []
        self.errmsg = self.zd.set_guestaccess_policy(**self.guestaccess_cfg)
        hlp.remove_all_restricted_subnet_entries(self.zd)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self.passmsg = "Create the guestaccess policy successufully."
        passmsg.append(self.passmsg)
        logging.info(self.passmsg)
        self._update_carrier_bag()
        return self.returnResult('PASS', self.passmsg)
        
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.guestaccess_cfg = dict(use_guestpass_auth = True,
                               enable_share_guestpass = False,
                               use_tou = True,
                               redirect_url = 'http://www.example.net/')
        self.guestaccess_cfg.update(conf)
        
        
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_guestaccess_policy'] = self.guestaccess_cfg
        