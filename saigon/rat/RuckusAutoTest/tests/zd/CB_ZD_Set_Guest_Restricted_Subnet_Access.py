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

class CB_ZD_Set_Guest_Restricted_Subnet_Access(Test):
    '''
    create the guest restricted subnet access on zd
    '''
    required_components = ['ZoneDirector', 'RuckusAP']
    parameter_description = {}
    
    def config(self, conf):
        self._init_test_params(conf)
    
        
    def test(self):
        self._create_restricted_subnet_access_list()
        if self.errmsg:
            return self.returnResult("FAIL", self.errmsg)
        self.passmsg = "Configure the guest restricted subnet access successufully."
        logging.info(self.passmsg)
        self._update_carrier_bag()
        return self.returnResult("PASS", self.passmsg)
        
    
    def cleanup(self):
        pass
    
    
    def _init_test_params(self, conf):
        self.guest_restricted_subnet_dict = {'restricted_subnet_list': []}
        self.guest_restricted_subnet_dict.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
        
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_restricted_subnet_list'] = \
        self.guest_restricted_subnet_dict['restricted_subnet_list']
        
    
    def _create_restricted_subnet_access_list(self):
        try:
            logging.info("Configure the guest restricted subnet access on ZD")
            self.zd.set_restricted_subnets(self.guest_restricted_subnet_dict['restricted_subnet_list'])
        except Exception, ex:
            self.errmsg = '[Configure the guest restricted subnet list failed] %s' % ex.message
            
