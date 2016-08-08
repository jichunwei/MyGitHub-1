'''
Description:
Created on 2010-8-4
@author: cwang@ruckuswireless.com    
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
class CB_Scaling_Remove_AAA_Servers(Test):
    '''
    All of AAA servers have been deleted.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        lib.zd.aaa.remove_all_servers(self.zd)
        self._update_carrier_bag()        
        return self.returnResult("PASS", "All of AAA servers have been deleted")
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        if self.testbed.components.has_key('ZoneDirector'):
            self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']     
        self.errmsg = ''
        self.passmsg = ''
    
