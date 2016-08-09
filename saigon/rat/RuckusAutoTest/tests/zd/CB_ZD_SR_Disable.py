"""
description:
    created by Louis
    Disable Smart Redundancy
    Modified by West,add disable SR on one zd function 
    
"""
#import os
#import re
import time
#import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.lib.zd import redundancy_zd
#from RuckusAutoTest.components import Helper_ZD as zhlp
from RuckusAutoTest.common import lib_Debug as bugme 

class CB_ZD_SR_Disable(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.disable_smart_redundancy()
        if self.errmsg:
            return ('FAIL', self.errmsg)
        msg = 'Disable Smart Redundancy '
        return ('PASS', msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf=conf
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']

    def disable_smart_redundancy(self):
        if not self.conf.has_key('single'):
            redundancy_zd.disable_pair_smart_redundancy(self.zd1, self.zd2)
        elif self.conf['single']:
            redundancy_zd.disable_single_smart_redundancy(self.carrierbag[self.conf['single']])
        else:
            redundancy_zd.disable_single_smart_redundancy(self.testbed.components['ZoneDirector'])
            time.sleep(30)
   
