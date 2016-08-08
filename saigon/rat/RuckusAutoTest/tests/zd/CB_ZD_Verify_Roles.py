'''
Description:
Created on 2010-8-10
@author: cwang@ruckuswireless.com
    config:
        
    test:
    
    cleanup:
    
'''
from RuckusAutoTest.models import Test

class CB_ZD_Verify_Roles(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        self.c_role_list = self.zd.get_role()
        for role in self.role_list:
            if not self.c_role_list.__contains__(role):
                self.returnResult("FAIL", "Role [%s] haven't existed in list" % role)
        self.passmsg = "All of roles are existed"
        self._update_carrier_bag()
        
        return self.returnResult("PASS", self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        self.role_list = self.carrierbag['existed_role_list']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        
        self.errmsg = ''
        self.passmsg = ''
    
