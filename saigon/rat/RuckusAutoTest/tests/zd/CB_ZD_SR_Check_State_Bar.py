'''
Created on 2010-7-2

@author: louis.lou@ruckuswireless.com
'''
#import os
#import re
#import time
import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.zd import redundancy_zd as red
#from RuckusAutoTest.components import Helper_ZD as zhlp


class CB_ZD_SR_Check_State_Bar(Test):
    '''
    classdocs
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        self.check_state_bar(self.active_zd)
        self.check_state_bar(self.standby_zd)
               
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        self.passmsg = 'The State bar show Correct'
        return self.returnResult('PASS', self.passmsg)
    
    
    def cleanup(self):
        pass

     

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.passmsg = ''
        self.conf = dict(
                          
                         )
        
        self.conf.update(conf)
                
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']
        
        
    def check_state_bar(self,zd):
        state = red._get_smart_redundancy(zd)
        if red.get_local_device_state(zd) == 'active':
            self.expect_result = 'Smart Redundancy: Active / Standby'
        else:
            self.expect_result = 'Smart Redundancy: Standby / Active'

        if state == self.expect_result:
            return True
        else:
            self.errmsg = 'The ZD %s state bar shows wrong message: %s instead %s' %(zd.ip_addr,state,self.expect_result)
            return False
