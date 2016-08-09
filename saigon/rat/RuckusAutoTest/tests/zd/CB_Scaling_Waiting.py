'''
Description:Waiting action which is used for sleep.
Created on 2010-8-3
@author: cwang@ruckuswireless.com
'''
import time
import logging

from RuckusAutoTest.models import Test

class CB_Scaling_Waiting(Test):
    '''
    Waiting action which is used for sleep, default sleep half an hour [1800 seconds].
    '''
    def config(self, conf):
        self._init_test_params(conf)
        self._retrive_carrier_bag()
    
    def test(self):
        start_time = time.time()
        end_time = time.time()
        elapsed_time = end_time - start_time
        while elapsed_time < self.chk_time_out:
            logging.info('Elapsed time is [%d], left time [%d]' % (elapsed_time, self.chk_time_out - elapsed_time))
            time.sleep(60)
            end_time = time.time()
            elapsed_time = end_time - start_time

        self._update_carrier_bag()
        self.passmsg = 'Have waited for [%d] seconds' % self.conf['timeout']        
        return self.returnResult('PASS', self.passmsg)
    
    def cleanup(self):
        pass
    
    def _retrive_carrier_bag(self):
        pass
    
    def _update_carrier_bag(self):
        pass
    
    def _init_test_params(self, conf):
        self.conf = dict(timeout = 1800)
        self.conf.update(conf)
        self.chk_time_out = self.conf['timeout']
        self.errmsg = ''
        self.passmsg = ''
    
