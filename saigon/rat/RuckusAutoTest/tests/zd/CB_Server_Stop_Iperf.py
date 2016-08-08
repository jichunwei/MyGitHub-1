'''
Created on Jun 19, 2014

@author: chen.tao@odc-ruckuswirelesss.com
'''

import logging
import time
from RuckusAutoTest.models import Test


class CB_Server_Stop_Iperf(Test):
    
    def _init_params(self, conf):
        self.conf = {}
        self.conf.update(conf)
        self.server = self.testbed.components['LinuxServer']       
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
        pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        try:    
            logging.info('Trying to stop Iperf server on LinuxPC')        
            self.server.stop_iperf()
        except Exception, ex:
            return self.returnResult('FAIL', ex.message)
        
        return self.returnResult('PASS', '')
    
    def cleanup(self):
        self._update_carribag()