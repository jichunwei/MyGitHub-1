'''
Description:
Created on 2010-8-18
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
from RuckusAutoTest.models import Test

class CB_ZD_Remove_All_Maps(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        self.zd.delete_all_maps()
        self._update_carrier_bag()
        return self.returnResult('PASS', 'All of maps have been deleted successfully')
    
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
    
