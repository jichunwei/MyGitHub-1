'''
Description:
Remove all the users from webui
Created on 2010-9-1
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import user

class CB_ZD_Remove_All_Users(Test):
    '''
    Remove all the users from webui.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        user.delete_all_users(self.zd)
        self._update_carrier_bag()
        
        return self.returnResult("PASS", "All of users have been deleted successfully")
    
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
    
