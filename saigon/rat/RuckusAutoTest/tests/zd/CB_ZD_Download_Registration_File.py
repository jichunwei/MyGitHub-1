'''
Download Registration File
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import admin_registration


class CB_ZD_Download_Registration_File(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        if admin_registration.download_reg_file(self.zd):
            return ('PASS', self.pass_msg)
        else:
            return ('FAIL', self.error_msg)
        
    def cleanup(self):
        pass


    def _cfgInitTestParams(self,conf): 
        self.errmsg=''
        self.zd = self.testbed.components['ZoneDirector']
        if self.carrierbag.has_key('active_zd'):
            self.zd = self.carrierbag['active_zd']
        self.pass_msg = 'download registration file successfully'
        self.error_msg = 'download registration file failed'
