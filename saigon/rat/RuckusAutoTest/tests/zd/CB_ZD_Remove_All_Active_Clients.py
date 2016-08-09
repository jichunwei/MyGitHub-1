'''
Description:
    Remove all the active clients
Created on 2010-9-1
@author: cwang@ruckuswireless.com
'''
import logging
import time
from RuckusAutoTest.models import Test

class CB_ZD_Remove_All_Active_Clients(Test):
    '''
    Remove all the active clients.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        self.zd.remove_all_active_clients()
        time.sleep(5)
        self._update_carrier_bag()
        
        return self.returnResult("PASS", self.passmsg)
    
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
    
