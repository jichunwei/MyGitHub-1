'''
Created on 2010-6-25

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
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_SR_Check_Version(Test):
    '''
    Check the ZD's version, if zd's version is the same as expected, return PASS
    
    else return FAIL
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        if self.zd_type == 'standby':
            self.check_version(self.standby_zd)
        elif self.zd_type == 'active':
            self.check_version(self.active_zd) 
        elif self.zd_type == 'zd1':
            self.check_version(self.zd1) 
        elif self.zd_type == 'zd2':
            self.check_version(self.zd2) 
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        msg = 'the version number is correct'
        return self.returnResult('PASS', msg)
    
    
    def cleanup(self):
        pass

     

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         zd_type = 'standby',
                         expect_version = ''
                         )
        
        self.conf.update(conf)
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
        self.active_zd = self.carrierbag['active_zd']
        self.standby_zd = self.carrierbag['standby_zd']
        self.zd_type = self.conf['zd_type']
        
        self.expect_version = self.conf['expect_version']
        
        if self.conf.has_key('build'):
            if self.conf['build']=='base':
                self.expect_version = self.carrierbag['base_build_version']
            else:
                self.expect_version = self.carrierbag['target_build_version']
        
        
    def check_version(self,zd):
        
        zd.login()
        zd.navigate_to(zd.ADMIN,zd.ADMIN_UPGRADE)
        version = zd._get_version()
        current_version = version['version']
        if current_version == self.expect_version:
            self.msg = 'The current version %s and the expect version are same' % current_version
        else:
            self.errmsg = 'The current version %s was not the expect version %s' % (current_version, self.expect_version)
        