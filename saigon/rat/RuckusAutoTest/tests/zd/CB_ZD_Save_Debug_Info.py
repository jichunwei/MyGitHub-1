'''
Download system log
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import admin_diagnostics


class CB_ZD_Save_Debug_Info(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        if admin_diagnostics.save_dbg_info(self.zd):
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
        self.pass_msg = 'save debug info successfully'
        self.error_msg = 'save debug info failed'
