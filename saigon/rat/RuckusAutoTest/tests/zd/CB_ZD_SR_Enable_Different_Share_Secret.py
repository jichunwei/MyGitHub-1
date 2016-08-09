#import os
#import re
import time
import logging
import random

from RuckusAutoTest.models import Test
#from RuckusAutoTest.components.ZoneDirector import ZoneDirector
from RuckusAutoTest.components.lib.zd import redundancy_zd
#from RuckusAutoTest.components import Helper_ZD as zhlp

class CB_ZD_SR_Enable_Different_Share_Secret(Test):
    
    def config(self,conf):
        self._cfgInitTestParams(conf)
    
    def test(self):
        self.test_different_share_secret()
        if self.errmsg:
            return self.returnResult('FAIL', self.errmsg)
        msg = 'Can NOT become a pair of Smart Redundancy ZD when using different share secret'
        return self.returnResult('PASS', msg)
    
    def cleanup(self):
        pass

        
    def _cfgInitTestParams(self, conf):
        self.errmsg = ''
        
        self.zd1 = self.carrierbag['zd1']
        self.zd2 = self.carrierbag['zd2']
        self.share_secret = self.carrierbag['share_secret'] 
#        self.different_share_secret = self.share_secret + 'testing'
        self.different_share_secret = self._generate_secret_key(random.randint(1,15))
        while True:
            if self.share_secret == self.different_share_secret:
                self.different_share_secret = self._generate_secret_key(random.randint(1,15))
            else:
                break
        
    def _generate_secret_key(self,n):
        al=list('abcdefghijklmnopqrstuvwxyz0123456789') 
        st='' 
        for i in range(n):
            index = random.randint(0,35) 
            st = st + al[index] 
        return st
        
    def test_different_share_secret(self):
        logging.info('Make sure 2 ZD can NOT become a pair smart redundancy ZD with different share secret')
        redundancy_zd.enable_single_smart_redundancy(self.zd1, self.zd2.ip_addr, self.share_secret) 
        redundancy_zd.enable_single_smart_redundancy(self.zd2, self.zd1.ip_addr, self.different_share_secret)
        timeout = 30
        start_time = time.time()
        while True:
            if redundancy_zd.get_local_device_state(self.zd1) == 'shared secret mismatched':
                logging.info("correct behavior, the shared secret mismatched, so it is not a pair smart redundancy ZD")
            
            if redundancy_zd.get_local_device_state(self.zd1) == 'active':
                if redundancy_zd.get_local_device_state(self.zd2) =='standby': 
                    logging.info('Incorrect behavior -- Enable smart redundancy successfully, and the ZD1 %s is the active ZD' % self.zd1.ip_addr)
                    return ('FAIL','')
                    
            elif redundancy_zd.get_local_device_state(self.zd1) =='standby': 
                if redundancy_zd.get_local_device_state(self.zd2) =='active':
                    logging.info('Incorrect behavior -- Enable smart redundancy successfully, and the ZD2 %s is the active ZD' % self.zd2.ip_addr)
                    return ("FAIL",'')
                
            if time.time() - start_time > timeout:
                logging.info("The 2 ZD don't be enable smart redundancy after %d seconds--Correct behavior", timeout)
                break
        
            
       
