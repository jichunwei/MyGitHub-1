'''
Description:
Created on 2010-10-27
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test

class CB_ZD_Set_Admin_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):                
        try:
            self.zd.set_admin_cfg(self.conf)
        except Exception, e:
            return self.returnResult('FAIL', e.message)
        
        self.admin_cfg = self.zd.get_admin_cfg()
        if self.admin_cfg['admin_name']:
            self.zd.username = self.admin_cfg['admin_name']
            self.zdcli.username = self.zd.username
            
        if self.admin_cfg['admin_pass1']:
            self.zd.password = self.admin_cfg['admin_pass1']
            self.zdcli.password = self.zd.password
        else:
            self.admin_cfg['admin_pass1'] = self.conf['admin_pass1']
            self.zd.password = self.admin_cfg['admin_pass1']
            
        self._update_carrier_bag()
        return self.returnResult('PASS', 'Set admin info correctly')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_admin_cfg'] = self.admin_cfg 
    
    def _init_test_params(self, conf):
        self.conf = dict(auth_method = 'local',
                         admin_name = 'admin',
                         admin_old_pass = 'admin',
                         admin_pass1 = 'admin',
                         admin_pass2 = 'admin')
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.zdcli = self.testbed.components['ZoneDirectorCLI']        
        self.errmsg = ''
        self.passmsg = ''