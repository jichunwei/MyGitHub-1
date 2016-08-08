'''
Description:
remove a list of roles
by west
    
'''
import logging

from RuckusAutoTest.models import Test

class CB_ZD_Remove_Roles(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self.zd.delete_roles(self.role_list)
        
        self._update_carrier_bag()
        self.passmsg = "Roles delete successfully"
        passmsg.append(self.passmsg)
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
        if self.testbed.components.has_key('ZoneDirector'):
            self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        self.role_list=self.conf['role_list']
        self.errmsg = ''
        self.passmsg = ''
    
