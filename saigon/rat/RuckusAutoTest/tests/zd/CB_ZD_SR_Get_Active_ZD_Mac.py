'''
get active and stanyby zd mac address
by west.li
'''

import time
import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd as red

class CB_ZD_SR_Get_Active_ZD_Mac(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
        
    def test(self):
        self.active_zd_mac=self._get_zd_mac_addr(self.active_zd)
        logging.info('zctive zd mac got:%s' % self.active_zd_mac)
        self.standby_zd_mac=self._get_zd_mac_addr(self.standby_zd)
        logging.info('standby zd mac got:%s' % self.standby_zd_mac)
        self._update_carrier_bag()
        
        return 'PASS','active zd mac:%s,standby zd mac:%s'%(self.active_zd_mac,self.standby_zd_mac)
    
    def cleanup(self):
        pass
        
    def _cfgInitTestParams(self,conf):
        self.active_zd=self.carrierbag['active_zd']
        self.standby_zd=self.carrierbag['standby_zd']
        
    def _get_zd_mac_addr(self,zd):
#        zd.navigate_to(zd.ADMIN, zd.ADMIN_PREFERENCE)
        return zd.mac_addr if zd.mac_addr else zd.get_mac_address()
    
    def _update_carrier_bag(self):
        self.carrierbag['active_zd_mac'] = self.active_zd_mac
        self.carrierbag['standby_zd_mac'] = self.standby_zd_mac