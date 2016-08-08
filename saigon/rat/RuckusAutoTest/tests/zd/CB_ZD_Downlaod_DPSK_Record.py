'''
Download DPSK record
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import wlan_zd


class CB_ZD_Downlaod_DPSK_Record(Test):

    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        if wlan_zd.download_dpsk_record(self.zd):
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
        self.pass_msg = 'download dpsk record successfully'
        self.error_msg = 'download dpsk record failed'
