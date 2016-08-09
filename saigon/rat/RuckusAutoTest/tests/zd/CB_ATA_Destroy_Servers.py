'''
Created on Nov 14, 2013

@author: cwang@ruckuswireless.com
'''

import logging
import time

from RuckusAutoTest.models import Test

class CB_ATA_Destroy_Servers(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict(servers=[])
        self.conf.update(conf)
        self.ata = self.testbed.components['ATA']
        self.servers = self.conf.get('servers')        
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
    
    def test(self):
        cnt = 0
        for server in self.servers:
            self.ata.destroy_server(**server)
            logging.info("Close server %s DONE" % server)
            cnt += 1
            time.sleep(cnt if cnt < 3 else  3)
        
        
        return self.returnResult('PASS', 'All of Server closed')
    
    def cleanup(self):
        self._update_carribag()
                

