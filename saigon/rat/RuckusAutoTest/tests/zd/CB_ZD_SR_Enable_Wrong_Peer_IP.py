#import os
#import re
import time
import logging

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.lib.zd import redundancy_zd
#from RuckusAutoTest.components import Helper_ZD as zhlp
import RuckusAutoTest.common.lib_Debug as bugme 

class CB_ZD_SR_Enable_Wrong_Peer_IP(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.test_wrong_peer_ip()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        msg = 'Can NOT become a pair of Smart Redundancy ZD when using wrong peer IP address'
        return self.returnResult('PASS', msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
        self.share_secret = self.carrierbag['share_secret'] 
        self.ip_addr = conf['ip_addr']
        
    def test_wrong_peer_ip(self):
        pause = 5
        timeout = 30
        redundancy_zd.enable_single_smart_redundancy(self.zd1, self.ip_addr, self.share_secret) 
        redundancy_zd.enable_single_smart_redundancy(self.zd2, self.ip_addr, self.share_secret)
        start_time = time.time()
        while True:
            if redundancy_zd.get_peer_device_state(self.zd1) == 'disconnected':
                if redundancy_zd.get_peer_device_state(self.zd2) == 'disconnected':
                    logging.info("Correct behavior, the peer IP disconnected, so it is not a pair smart redundancy ZD")
                    break
            elif redundancy_zd.get_peer_device_state(self.zd1).find('mismatched'):
                logging.info("Correct behavior, the peer IP mismatched, so it is not a pair smart redundancy ZD")
                break
            elif redundancy_zd.get_local_device_state(self.zd1) == 'active':
                if redundancy_zd.get_local_device_state(self.zd2) =='standby': 
                    self.errmsg = 'Incorrect behavior -- Enable smart redundancy successfully, and the ZD1 %s is the active ZD' % self.zd1.ip_addr
                    return self.errmsg
                    
            elif redundancy_zd.get_local_device_state(self.zd1) =='standby': 
                if redundancy_zd.get_local_device_state(self.zd2) =='active':
                    self.errmsg = 'Incorrect behavior -- Enable smart redundancy successfully, and the ZD2 %s is the active ZD' % self.zd2.ip_addr
                    return self.errmsg
            else:
                time.sleep(pause)
                    
            if time.time() - start_time > timeout:
                logging.info("The 2 ZD don't be enable smart redundancy after %d seconds", timeout)
                break
        
            
       
