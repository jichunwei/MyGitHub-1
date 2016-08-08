'''
Description:
Created on 2010-11-5
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test

class CB_ZD_Get_System_Name(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        self.sys_name = self.zd.get_system_name()
        self._update_carrier_bag()        
        return self.returnResult('PASS', 'System name [%s]' % self.sys_name)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_sys_name'] = self.sys_name
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
