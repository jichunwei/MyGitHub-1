'''
Description:
by West
verify the admin info is the same as expected
'''
from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd.admin_preference import get_admin_cfg
class CB_ZD_Verify_Admin_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
        
    def test(self):        
        info=get_admin_cfg(self.zd)
        for key in self.conf:
            if (key in info) and (self.conf[key]!=info[key]):
                self.errmsg+='%s(%s) not the same as expected(%s),'%(key,info[key],self.conf[key])
        
        for key in info:
            if (info[key] is not None) and (not key in self.conf):
                self.errmsg+='unexpected key:%s(%s) get'%(key,info[key])
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        else:        
            self._update_carrier_bag()
            return self.returnResult('PASS', 'verify admin Info successfully')
    
    def cleanup(self):
        pass
    
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
         }
        '''
        self.conf = {
                     }
        self.conf.update(conf)        
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
        
