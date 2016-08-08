'''
Created on Oct 15, 2013

@author: cwang@ruckuswireless.com
'''

import logging

from RuckusAutoTest.models import Test

from RuckusAutoTest.components.lib.zd import statistic_report as STR


class CB_ATA_Purge_ENV(Test):
    required_components = ['ATA']
    parameters_description = {}
    
    def _init_params(self, conf):
        self.conf = dict()
        self.conf.update(conf)        
        self.ata = self.testbed.components['ATA']
        logging.info('=========Initialize ENV DONE=========')
    
    def _retrieve_carribag(self):
        pass
    
    def _update_carribag(self):
         pass
     
    def config(self, conf):
        self._init_params(conf)
        self._retrieve_carribag()
        logging.info("==========Configure Parameter DONE==========")
    
    def test(self):
        self.ata.remove_ports()        
        return self.returnResult('PASS', 'Clean up ATA ENV, DONE.')
    
    def cleanup(self):
        self._update_carribag()