'''
Description:
verify the Privilege Level of user is the same as expected
1. get the privilege level according to the xpath in web
2. verify the level is the same as expected
3. verify the priority is correct

by west
'''

import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components import Helpers

class CB_ZD_Verify_Privilege_Level(Test):
    
    ADMIN_RESTART_LOCATORS = dict(
        #in Administrator page
        restart_button = "//input[@id='restart']",
    )
    
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        level = self._get_privilege_level()
        if 'error'==level:
            return ('FAIL','get privilege level error')
        if level!=self.conf['level']:
            return ('FAIL',"the level(%s) is not the same to expected(%s)"%(level,self.conf['level']))
        
        return self.returnResult('PASS', "the level(%s) is the same to expected"%self.conf['level'])
    
    def cleanup(self):
        self._update_carribag()
        
    def _init_params(self, conf):
        self.conf = {'level':'super',#operator,monitor
                     }
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.xloc=self.ADMIN_RESTART_LOCATORS
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def _get_privilege_level(self):
        self.zd.navigate_to(self.zd.ADMIN, self.zd.ADMIN_RESTART)
        super=False
        monitor= False
        if self.zd.s.is_element_visible(self.xloc['restart_button']):
            super=True
        if self.zd.s.is_element_present(self.zd.DISABLED_CONFIGURE):
            monitor=True
        if super and monitor:
            res= 'error'
        else:
            if super:
                res='super'
            elif monitor:
                res='monitor'
            else:
                res='operator'
        return res

        
    
