'''
Description:
    config:
        
    test:
    
    cleanup:
    
Created on 2010-6-11
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test

class CB_ZD_Remove_Local_User(Test):
    '''
    Test case for automation.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        self.zd.delete_user(self.username)
        
        current_user_list = self.zd.get_user()
        found = False
        
        for user in current_user_list:
            if user == self.username:
                found = True
                break
        if found:
            self.errormsg = "user[%s] haven't been deleted correctly." % self.username
            logging.info(self.errormsg)
            return ['FAIL', self.errormsg]
        
        else:
            self.passmsg = "user[%s] delete successfully" % self.username
            logging.info(self.passmsg)            
            passmsg.append(self.passmsg)
                               
        self._update_carrier_bag()
        
        return ["PASS", passmsg]
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        if self.carrierbag.has_key('existed_username'):
            self.username = self.carrierbag['existed_username']        
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(username='rat_guest_pass')
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.username = self.conf['username']
        self._retrive_carrier_bag()
        self.passmsg = ""
        self.errormsg = ""
        
    
