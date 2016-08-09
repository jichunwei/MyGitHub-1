'''
Description:
    config:
        
    test:
    
    cleanup:
    
Created on 2010-6-10
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test

class CB_ZD_Remove_All_DPSK(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._retrive_carrier_bag()
        self._init_test_params(conf)
        
    
    def test(self):
        passmsg = []
        
        logging.info("Remove all Generated PSKs on the ZD")
        self.zd._remove_all_generated_psks()
        self.passmsg = 'all of psks have been deleted.'
        passmsg.append(self.passmsg)
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
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
