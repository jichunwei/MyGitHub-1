'''
by West.li@2012.2.2
get the mac address of zd2 in testbed
'''

import logging
from RuckusAutoTest.models import Test

class CB_ZD_Get_ZD2_Mac(Test):
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.zd2.navigate_to(self.zd2.ADMIN, self.zd2.ADMIN_PREFERENCE)
        mac_address2 = self.zd2.mac_addr
        self.carrierbag['zd2_mac']=mac_address2
        self.passmsg= 'zd2 mac addr is %s' % mac_address2
        
        self.zd1.navigate_to(self.zd1.ADMIN, self.zd1.ADMIN_PREFERENCE)
        mac_address1 = self.zd1.mac_addr
        self.carrierbag['zd1_mac']=mac_address1
        self.passmsg+= ',zd1 mac addr is %s' % mac_address1
        
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.passmsg= ''
        self.zd2 = self.testbed.components['zd2']  
        self.zd1 = self.testbed.components['zd1']  
        
        