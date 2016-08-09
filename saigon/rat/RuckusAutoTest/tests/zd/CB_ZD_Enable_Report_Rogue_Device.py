# Copyright (C) 2009 Ruckus Wireless, Inc. All rights reserved.
"""
triger rogue dhcp alarm by 
disable Rogue DHCP Server Detection and enable Rogue DHCP Server Detection
in wips configuration page
   - 
"""
import logging
import time
from RuckusAutoTest.components.lib.zd import wips_zd as wips

from RuckusAutoTest.models import Test

class CB_ZD_Enable_Report_Rogue_Device(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)
        
    def test(self):      
        wips.enable_wips_report_rogue_devices(self.zd)
        logging.info('enable report rogue device successfully')
        passmsg = 'enable report rogue device successfully' 
        return self.returnResult('PASS', passmsg)
        
    def cleanup(self):
        pass
    
    def _cfgInitTestParams(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
