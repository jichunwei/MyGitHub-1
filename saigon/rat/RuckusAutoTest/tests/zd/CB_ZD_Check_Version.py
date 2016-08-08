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

class CB_ZD_Check_Version(Test):
    '''
    Check the ZD's version, if zd's version is the same as expected, return PASS
    
    else return FAIL
    '''
    def config(self,conf):
        self._cfg_init_test_params(conf)
    
    def test(self):
        self.check_version(self.zd) 
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        
        return self.returnResult('PASS', self.msg)
    
    
    def cleanup(self):
        pass

     

    def _cfg_init_test_params(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         expect_version = ''
                         )
        
        self.conf.update(conf)
        self.zd = self.testbed.components['ZoneDirector']
        self.use_cli = False
        zd=self.conf.get('zd')
        if zd:
            self.zd = self.carrierbag[zd]
        
        cli = self.conf.get('zdcli')
        if cli:
            self.zdcli = self.carrierbag[cli]
            self.use_cli = True
        self.expect_version = self.conf['expect_version']
        if self.conf.has_key('build'):
            if self.conf['build']=='base':
                self.expect_version = self.carrierbag['base_build_version']
            else:
                self.expect_version = self.carrierbag['target_build_version']
        
        
    def check_version(self,zd):
        if not self.use_cli:
            logging.info('get version from web')
            zd.login()
            zd.navigate_to(zd.ADMIN,zd.ADMIN_UPGRADE)
            version = zd._get_version()
        else:
            logging.info('get version from cli')
            version = self.zdcli._get_version()
        current_version = version['version']
        
        if current_version == self.expect_version:
            self.msg = 'The current version %s and the expect version are same' % current_version
        else:
            self.errmsg = 'The current version %s was not the expect version %s' % (current_version, self.expect_version)
        