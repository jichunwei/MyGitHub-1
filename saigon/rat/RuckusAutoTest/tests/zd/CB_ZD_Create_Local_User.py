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
from RuckusAutoTest.components.lib.zd import user

class CB_ZD_Create_Local_User(Test):
    '''
    create local user under zd.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        passmsg = []
        res = user.get_user(self.zd, self.username, is_nav = True)        
        if res:
            self.zd.delete_user(self.username)
            
        self.zd.create_user(self.username, self.password, fullname = self.fulname, role = self.role, )        
        self.passmsg = "Create user[%s], password[%s] successfully" % (self.username, self.password)
        passmsg.append(self.passmsg)
        logging.info( self.passmsg )
        self._update_carrier_bag()
        
        return self.returnResult("PASS", passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_username'] = self.username 
        self.carrierbag['existed_password'] = self.password 
    
    def _init_test_params(self, conf):
        self.conf = dict(username = 'admin',
                         password = 'admin',
                         fullname = '',
                         role = 'Default',)
        self.conf.update(conf)
        
        self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        
        self.username = self.conf['username']
        self.password = self.conf['password']
        self.fulname = self.conf['fullname']
        self.role = self.conf['role']
        self.passmsg = ''
        self.errmsg = ''
        