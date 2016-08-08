'''
Description:
    config:
        
    test:
    
    cleanup:
    
Created on 2010-7-27
@author: cwang@ruckuswireless.com
'''
import logging

from RuckusAutoTest.models import Test

class CB_ZD_Verify_System_Name(Test):
    
    def config(self, conf):        
        self._init_test_params(conf)
        
    
    def test(self):
        self._verify_system_name(self.zd)
        
        if self.errmsg:
            return ("FAIL",self.errmsg)
        
        else:
            return('PASS',self.passmsg)
    
    def cleanup(self):
        pass
    
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(system_name_change = True, before_system_name ='')
        self.before_system_name = self.conf['before_system_name']
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
       
        self.passmsg = ""
        self.errmsg = ""
    
    
    def _verify_system_name(self,zd):
        current_system_name = zd.get_system_name()
        if not self.conf['system_name_change']:
            if current_system_name == 'Ruckus':
                self.passmsg = 'System name does not restore'
            else:
                self.errmsg = 'System name restore'
        
        else:
            if current_system_name == self.before_system_name:
                self.passmsg = 'System name restore'
            else:
                self.errmsg = 'System name does not restore'
            
