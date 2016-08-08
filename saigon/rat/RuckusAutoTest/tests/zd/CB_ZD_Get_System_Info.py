'''
Description:Get system info from ZD's GUI
Created on 2010-11-3
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import dashboard_zd

class CB_ZD_Get_System_Info(Test):
    '''
    Get system info from ZD's GUI dash board.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):                
        self.sys_info = dashboard_zd.get_system_info(self.zd)
        self._update_carrier_bag()
        return self.returnResult('PASS', 'Get system information correctly.')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_sys_info'] = self.sys_info
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
