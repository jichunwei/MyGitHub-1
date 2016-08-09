'''
Description:
    Verify Current guest passes record are empty.
Created on 2010-8-31
@author: cwang@ruckuswireless.com    
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib

class CB_Scaling_Verify_Guest_Passes_Empty(Test):
    '''
    Verify Current Guest passes record are empty.    
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        total = int(lib.zd.ga.get_all_guestpasses_total_numbers(self.zd))
        if total > 0:
            return self.returnResult("FAIL", "GuestPasses are not empty")
        self._update_carrier_bag()
        
        return self.returnResult("PASS", "GuestPasses are empty")
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
