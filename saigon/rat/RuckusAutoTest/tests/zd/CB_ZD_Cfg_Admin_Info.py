'''
Description:
by West
config admin infomation
'''
from RuckusAutoTest.models import Test
class CB_ZD_Cfg_Admin_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
    def test(self):        
        self.zd.set_admin_cfg(self.conf)
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:        
            self._update_carrier_bag()
            return self.returnResult('PASS', 'Set admin Info successfully')
    
    def cleanup(self):
        self.zd.username = 'admin'
        self.zd.password = 'admin'
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        '''
        input
        {'auth_method':'local',
         'auth_server':'',
         'fallback_local':True,
         'admin_name':'',
         'admin_old_pass':'',
         'admin_pass1':'',
         'admin_pass2':''
         'login_info':{'re_login':True, 'username':'test5','password':'lab4man1'}
         }
        '''
        self.conf = {'auth_method':'local',#'local'/"external"
                     'auth_server':'',
                     }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if self.conf.has_key('login_info') and self.conf['login_info']['re_login']:
            self.zd.username = self.conf['login_info']['username']
            self.zd.password = self.conf['login_info']['password']
            self.zd.login()
        self.errmsg = ''
        self.passmsg = ''
        
