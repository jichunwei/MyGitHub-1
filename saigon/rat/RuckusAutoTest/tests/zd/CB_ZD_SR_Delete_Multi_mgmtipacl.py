'''
Description:
Created on 2010-7-16
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import mgmt_ip_acl

class CB_ZD_SR_Delete_Multi_mgmtipacl(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = ["All of mgmtipacl have been deleted"]
        mgmt_ip_acl.delete_all_mgmtipacl(self.active_zd)
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']         
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        
        self.errmsg = ''
        self.passmsg = ''
    
