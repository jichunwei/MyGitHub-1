'''
Description:
    created by Louis
    
    Get Standby ZD after enable Smart Redundancy.

    return self.carrierbag['standby_zd']

'''
#import os
#import re
#import time
#import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.RuckusAP import RuckusAP
from RuckusAutoTest.components.lib.zd import redundancy_zd as red
#from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_SR_Get_Standby_ZD(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.carrierbag['standby_zd'] = self.get_standby_zd(self.zd1,self.zd2)
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)

        msg = 'The Standby ZD is %s' % self.carrierbag['standby_zd'].ip_addr
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
       
    def get_standby_zd(self,zd1,zd2):
        if red.get_local_device_state(zd1) == 'standby':
            self.carrierbag['standby_mac'] = zd1.mac_addr
            self.carrierbag['standby_zd']= zd1
            self.carrierbag['standby_zd_cli']=self.carrierbag['zdcli1']
            return zd1
        else:
            self.carrierbag['standby_mac'] = zd2.mac_addr
            self.carrierbag['standby_zd']= zd2
            self.carrierbag['standby_zd_cli']=self.carrierbag['zdcli2']
            return zd2
