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
#import RuckusAutoTest.components.lib.zd.wips_zd as wips

from RuckusAutoTest.models import Test

class CB_ZD_Triger_Rogue_DHCP_Alarm(Test):
    
    def config(self, conf):
        self._cfgInitTestParams(conf)
        
    def test(self):      
        wips.disable_rogue_dhcp_server_detection(self.zd)
        logging.info('disable dhcp server dection successfully')
        time.sleep(2)
        wips.enable_rogue_dhcp_server_detection(self.zd)
        logging.info('enable dhcp server dection successfully')
        passmsg = 'disable enable rogue dhcp dection successfully' 
        return self.returnResult('PASS', passmsg)
        
    def cleanup(self):
        pass
    
    def _cfgInitTestParams(self, conf):
        self.zd = self.testbed.components['ZoneDirector']
