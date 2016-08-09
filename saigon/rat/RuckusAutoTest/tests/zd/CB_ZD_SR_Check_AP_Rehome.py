import logging

from RuckusAutoTest.models import Test
from RuckusAutoTest.components.lib.zd import redundancy_zd
from RuckusAutoTest.common import lib_Debug as bugme

class CB_ZD_SR_Check_AP_Rehome(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        if self.former_active[0] == self.former_standby[0]:
            self.errmsg = "The active ZD mac address are same"
        if self.former_active[1] != self.former_standby[1]:
            self.errmsg = "The APs DO NOT come back after 60 Seconds"
            
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        msg = 'AP Rehome Correctly during 60 Seconds'
        return self.returnResult('PASS', msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.conf = dict(
                         
                         )
        
        self.conf.update(conf)
        
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
#        self.share_secret = self.carrierbag['share_secret'] 
        self.former_active = self.carrierbag['former_active']
        self.former_standby = self.carrierbag['former_standby']
     
       
