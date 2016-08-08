'''
Description: Enable/Disable load-balancing from ZD GUI.
Created on 2010-10-27
@author: cwang@ruckuswireless.com
'''

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers as lib
from RuckusAutoTest.components.lib.zd import service_zd as sz

class CB_ZD_Set_Load_Balancing(Test):
    '''
    Enable/Disable load-balancing from ZD GUI.
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        if self.is_enable:        
            #lib.zd.ap.enable_load_balancing(self.zd)
            sz.enable_load_balancing(self.zd)
        else:                        
            sz.disable_load_balancing(self.zd)
            
        self._update_carrier_bag()
        return self.returnResult("PASS", 'Set load balancing to [%s] correctly' % self.is_enable)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(enable=True)
        self.conf.update(conf)
        self.is_enable = self.conf['enable']
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    