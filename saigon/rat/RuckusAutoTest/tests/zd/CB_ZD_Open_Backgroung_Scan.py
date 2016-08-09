# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
"""
triger rogue dhcp alarm by 
disable Rogue DHCP Server Detection and enable Rogue DHCP Server Detection
in wips configuration page
   - 
"""
import logging
import time
from RuckusAutoTest.components.lib.zd import service_zd as service

from RuckusAutoTest.models import Test

class CB_ZD_Open_Backgroung_Scan(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)
        
    def test(self):      
        service.set_background_scan_options(self.zd,self.conf['2_4'],self.conf['5'],)
        logging.info('open background scan successfully')
        passmsg = 'open background scan successfully' 
        return self.returnResult('PASS', passmsg)
        
    def cleanup(self):
        pass
    
    def _cfgInitTestParams(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
        self.conf={'2_4':'20',
                   '5':'20'}
        self.conf.update(conf)
        
