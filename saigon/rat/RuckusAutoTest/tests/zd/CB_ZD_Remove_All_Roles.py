'''
Description:
Created on 2010-8-10
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
import logging

from RuckusAutoTest.models import Test

class CB_ZD_Remove_All_Roles(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self.zd.remove_all_roles()
        self.role_list = self.zd.get_role()
        if len(self.role_list) > 1:
            self.errmsg = "Roles haven't deleted correctly, existed [%s]" % self.role_list
            self.returnResult("FAIL", self.errmsg)
            
        self._update_carrier_bag()
        self.passmsg = "Roles delete successfully"
        passmsg.append(self.passmsg)
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        if self.carrierbag.has_key('existed_role_list'):
            self.carrierbag['existed_role_list'] = self.role_list
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        if self.testbed.components.has_key('ZoneDirector'):
            self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        
        self.errmsg = ''
        self.passmsg = ''
    
