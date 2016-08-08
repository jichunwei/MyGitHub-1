'''
Description:
Created on 2010-11-5
@author: cwang@ruckuswireless.com
'''
from RuckusAutoTest.models import Test


class CB_ZD_Get_Sys_Interface_Info(Test):
    '''
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):        
        self.ip_cfg = self.zd.get_ip_cfg()
        self._update_carrier_bag()        
        return self.returnResult('PASS', 'Get IP configuration successfully')
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        self.carrierbag['existed_ip_cfg'] = self.ip_cfg
    
    def _init_test_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']        
        self.errmsg = ''
        self.passmsg = ''
    
