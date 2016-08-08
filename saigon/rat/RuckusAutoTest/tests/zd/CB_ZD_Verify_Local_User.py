'''
Description:
    Checking specify 'user' is existed.
    
Created on 2010-6-11
@author: cwang@ruckuswireless.com
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import user
class CB_ZD_Verify_Local_User(Test):
    '''
    Verify user exist in ZD.
    '''
    def config(self, conf):        
        self._init_test_params(conf)
        
    def test(self):        
        res = user.get_user(self.zd, self.username, is_nav = True)
        if res:
            self.passmsg = "user[%s] existed" % self.username
            return self.returnResult("PASS", self.passmsg)    
        else:
            self.errmsg = "user[%s] have not been found" % self.username
            return self.returnResult("FAIL", self.errmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('existed_username'):
            self.username = self.carrierbag['existed_username']
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(username='admin')
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.username = self.conf['username']
        self._retrive_carrier_bag()
        self.passmsg = ""
        self.errmsg = ""
        