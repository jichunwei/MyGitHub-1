'''
Description:
    Let AP Wait for <number> seconds, so that trigger action finish.
Create on 2013-8-7
@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test


class CB_AP_Wait_For(Test):
    required_components = ['']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(timeout=90)
        self.conf.update(conf)
        self.timeout = self.conf.get('timeout')
            
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        logging.info('Program pause for %d seconds' % self.timeout)
        time.sleep(self.timeout)
        
        return self.returnResult('PASS', 'Wait for %d seconds, DONE' % self.timeout)
    
    def cleanup(self):
        self._update_carribag()